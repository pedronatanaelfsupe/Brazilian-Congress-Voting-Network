import pandas as pd
import os
import networkx as nx
from A_data_aquisition import fetch_all_datasets
from B_data_pre_processing import (
    rename_columns,
    filter_votacoes,
    calculate_yes_vote_percentage,
    filter_polarized_votacoes
)
from C_modularity_optimization import (
    generate_graph, 
    save_graph,
    analyze_pruning,
    prune_graph,
    detect_communities
)

def determine_optimal_pruning(results):
    """
    Determines the optimal pruning percentage based on the criteria:
    - Minimum number of communities detected greater than one
    - Maximum modularity value

    Args:
        results (list): List of dictionaries containing pruning analysis results.

    Returns:
        float: The optimal pruning percentage.
    """
    # Filter results where number of communities > 1
    valid_results = [res for res in results if res['num_communities'] > 1]

    if not valid_results:
        print("No valid pruning percentage found where number of communities > 1.")
        return None

    # Find the minimum number of communities greater than one
    min_num_communities = min(res['num_communities'] for res in valid_results)

    # Filter results with the minimum number of communities
    min_community_results = [res for res in valid_results if res['num_communities'] == min_num_communities]

    # Find the maximum modularity among these results
    max_modularity = max(res['modularity'] for res in min_community_results)

    # Select the result with maximum modularity
    optimal_results = [res for res in min_community_results if res['modularity'] == max_modularity]

    # If multiple results have the same modularity, pick the one with the lowest pruning percentage
    optimal_result = min(optimal_results, key=lambda x: x['pruning_percentage'])

    optimal_pruning_percentage = optimal_result['pruning_percentage']
    print(f"Optimal pruning percentage determined: {optimal_pruning_percentage}%")
    return optimal_pruning_percentage

def data_acquisition():
    """
    Performs data acquisition by fetching all datasets.
    """
    fetch_all_datasets()
    print("Data acquisition completed.")

def data_processing():
    """
    Performs data processing steps including loading datasets,
    renaming columns, merging datasets, and filtering data.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    # Load datasets
    df_proposicao_microdados = pd.read_csv('data/csv/proposicao_microdados.csv')
    df_proposicao_tema = pd.read_csv('data/csv/proposicao_tema.csv')
    df_votacao_objeto = pd.read_csv('data/csv/votacao_objeto.csv')
    df_votacao = pd.read_csv('data/csv/votacao.csv')
    df_orgao_deputado = pd.read_csv('data/csv/orgao_deputado.csv')

    # Rename columns for consistency
    df_proposicao_microdados = rename_columns(df_proposicao_microdados, {'data': 'proposition_date', 'ano': 'proposition_year'})
    df_votacao_objeto = rename_columns(df_votacao_objeto, {'data': 'voting_date'})
    df_votacao_objeto['voting_date'] = pd.to_datetime(df_votacao_objeto['voting_date'])
    df_votacao_objeto['voting_year'] = df_votacao_objeto['voting_date'].dt.year

    # Merge datasets step by step using appropriate keys
    # Merge proposicao_microdados and proposicao_tema on 'id_proposicao'
    df_proposicao = pd.merge(
        df_proposicao_microdados[['id_proposicao', 'proposition_year', 'proposition_date', 'sigla', 'tipo']],
        df_proposicao_tema[['id_proposicao', 'tema']],
        on='id_proposicao',
        how='left'
    )

    # Merge the result with votacao_objeto on 'id_proposicao'
    df_proposicao_votacao = pd.merge(
        df_proposicao,
        df_votacao_objeto[['id_proposicao', 'id_votacao', 'voting_date', 'voting_year']],
        on='id_proposicao',
        how='left'
    )

    # Now merge with votacao on 'id_votacao'
    df_merged = pd.merge(
        df_proposicao_votacao,
        df_votacao[['id_votacao', 'sigla_orgao', 'aprovacao', 'voto_sim', 'voto_nao', 'voto_outro']],
        on='id_votacao',
        how='left'
    )

    # Filter out votacoes with null 'aprovacao'
    df_filtered = filter_votacoes(df_merged)

    # Calculate yes vote percentage
    df_filtered = calculate_yes_vote_percentage(df_filtered)

    # Number of propositions before the polarization filter
    num_propositions_before = df_filtered['id_proposicao'].nunique()

    print("Data processing completed.")

    return df_filtered, num_propositions_before, df_orgao_deputado

def optimize_polarization_interval(df_filtered, df_deputados, fixed_random_state):
    """
    Optimizes the polarization interval for each year to maximize modularity.
    Performs graph generation and community detection, including assigning node attributes.

    Args:
        df_filtered (pd.DataFrame): The DataFrame after initial filtering and yes vote percentage calculation.
        df_deputados (pd.DataFrame): DataFrame of deputy information.
        fixed_random_state (int): Random state for reproducibility.

    Returns:
        tuple: Final summary results and detailed results.
    """
    final_summary_results = []
    detailed_results = []

    # Step 3: Graph Generation
    df_votacao_parlamentar = pd.read_csv('data/csv/votacao_parlamentar.csv')

    # Convert 'voting_date' column to datetime and extract 'ano_votacao'
    df_votacao_parlamentar['data'] = pd.to_datetime(df_votacao_parlamentar['data'], errors='coerce')
    df_votacao_parlamentar['ano_votacao'] = df_votacao_parlamentar['data'].dt.year

    # Define years to analyze
    years = df_votacao_parlamentar['ano_votacao'].dropna().unique()

    for year in years:
        print(f"\nProcessing year: {year}")
        # Filter votes for the current year based on 'ano_votacao'
        df_votes_year = df_votacao_parlamentar[df_votacao_parlamentar['ano_votacao'] == year]

        # Define polarization intervals to test
        intervals = [(lower, 100 - lower) for lower in range(0, 50, 10)]  # E.g., (0,100), (2,98), ..., (48,52)

        best_modularity = -1
        best_interval = None
        best_results_summary = None

        for lower_bound, upper_bound in intervals:
            print(f"Testing polarization interval: {lower_bound}% - {upper_bound}%")
            # Filter polarized votacoes by 'ano_votacao'
            df_polarized = filter_polarized_votacoes(
                df_filtered[df_filtered['voting_date'].dt.year == year],
                lower_bound*0.01,
                upper_bound*0.01
            )

            if df_polarized.empty:
                print("No votacoes found for this interval.")
                continue

            # Keep only votes from selected votacoes
            df_votes = df_votes_year[df_votes_year['id_votacao'].isin(df_polarized['id_votacao'])]

            if df_votes.empty:
                print("No votes found for this interval.")
                continue

            # Generate graph
            G = generate_graph(df_votes, year)

            if G.number_of_edges() == 0:
                print("Graph has no edges.")
                continue

            # Analyze pruning with fixed random state
            pruning_percentages = list(range(0, 101, 2))
            results = analyze_pruning(G, pruning_percentages, random_state=fixed_random_state)

            # Automatically determine the optimal pruning percentage
            optimal_pruning_percentage = determine_optimal_pruning(results)

            if optimal_pruning_percentage is None:
                print("No optimal pruning percentage found.")
                continue

            # Prune the graph at the optimal pruning percentage
            G_optimal = prune_graph(G.copy(), optimal_pruning_percentage)

            if G_optimal.number_of_edges() == 0:
                print("Pruned graph has no edges.")
                continue

            # Detect communities on the pruned graph with a fixed random state
            communities, modularity = detect_communities(G_optimal, random_state=fixed_random_state)

            # Collect detailed results for plotting
            for res in results:
                detailed_results.append({
                    'Year': year,
                    'Polarization Lower Bound (%)': lower_bound,
                    'Polarization Upper Bound (%)': upper_bound,
                    'Pruning Percentage (%)': res['pruning_percentage'],
                    'Number of Communities': res['num_communities'],
                    'Modularity': res['modularity']
                })

            # Check if this modularity is the best for the year
            if modularity > best_modularity:
                best_modularity = modularity
                best_interval = (lower_bound, upper_bound)
                best_results_summary = {
                    'Year': year,
                    'Optimal Pruning Percentage (%)': optimal_pruning_percentage,
                    'Number of Communities': len(set(communities.values())),
                    'Modularity': modularity,
                    'Polarization Lower Bound (%)': lower_bound,
                    'Polarization Upper Bound (%)': upper_bound
                }
                # Save the best graph and communities
                best_G_optimal = G_optimal
                best_communities = communities

        if best_modularity == -1:
            print(f"No suitable interval found for year {year}.")
            continue

        print(f"Best polarization interval for year {year}: {best_interval[0]}% - {best_interval[1]}% with modularity {best_modularity:.4f}")

        # Assign communities to nodes
        nx.set_node_attributes(best_G_optimal, best_communities, 'community')

        # Assign additional node attributes
        party_orientation = {
            "PT": "esquerda",
            "PSOL": "esquerda",
            "PCdoB": "esquerda",
            "PL": "direita",
            "PP": "direita",
            "REPUBLICANOS": "centro-direita",
            "MDB": "centro",
            "PSB": "centro-esquerda",
            "PSD": "centro",
            "AGIR": "direita",
            "CIDADANIA": "centro-esquerda",
            "DC": "direita",
            "NOVO": "direita",
            "PCB": "esquerda",
            "PCO": "esquerda",
            "PDT": "centro-esquerda",
            "PMB": "direita",
            "PMN": "esquerda",
            "PODE": "centro-direita",
            "PRTB": "direita",
            "PSDB": "centro",
            "PV": "esquerda",
            "REDE": "esquerda",
            "SOLIDARIEDADE": "centro",
            "PSL": "centro-direita",
            "PR": "direita",
            "PTN": "direita",
            "AVANTE": "centro",
            "PMDB": "centro",
            "PRB": "direita",
            "PSC": "direita",
            "PTB": "direita",
            "PFL": "centro-direita",
            "DEM": "centro-direita",
            "UNIÃO": "centro-direita",
            "PPS": "esquerda",
            "PROS": "centro",
            "PATRIOTA": "direita",
            "PHS": "centro-direita",
            "PRP": "direita",
            "SD": "centro",
            "PPB": "direita",
            "PST": "centro-esquerda",
            "PTdoB": "centro",
            "PEN": "direita",
            "PRONA": "direita",
            "S.PART.": "Sem Partido",
            "PMR": "direita",
            "PTC": "direita",
            "SDD": "centro",
            "PSDC": "direita",
            "PATRI": "direita",
            "PAN": "centro"
        }

        for node in best_G_optimal.nodes():
            # Get deputy info
            deputado_info = df_deputados[df_deputados['id_deputado'] == node]
            if not deputado_info.empty:
                nome = deputado_info.iloc[0]['nome']
                sigla_partido = deputado_info.iloc[0]['sigla_partido']
                sigla_uf = deputado_info.iloc[0]['sigla_uf']
                orientation = party_orientation.get(sigla_partido, 'unknown')

                # Assign attributes
                best_G_optimal.nodes[node]['nome'] = nome
                best_G_optimal.nodes[node]['sigla_partido'] = sigla_partido
                best_G_optimal.nodes[node]['sigla_uf'] = sigla_uf
                best_G_optimal.nodes[node]['orientation'] = orientation
            else:
                print(f"Deputy info not found for id_deputado: {node}")
                best_G_optimal.nodes[node]['nome'] = 'Unknown'
                best_G_optimal.nodes[node]['sigla_partido'] = 'Unknown'
                best_G_optimal.nodes[node]['sigla_uf'] = 'Unknown'
                best_G_optimal.nodes[node]['orientation'] = 'unknown'

        # Save the graph with complete information
        graph_path_with_communities = f"data/graphs/graph_{year}_communities.gml"
        os.makedirs(os.path.dirname(graph_path_with_communities), exist_ok=True)
        save_graph(best_G_optimal, graph_path_with_communities)
        print(f"Graph with communities saved to {graph_path_with_communities}")

        # Collect final summary results
        final_summary_results.append(best_results_summary)

    return final_summary_results, detailed_results

def save_results(final_summary_results, detailed_results):
    """
    Outputs final summary results and detailed results, and saves them to CSV files.

    Args:
        final_summary_results (list): List of dictionaries containing summary results for each year.
        detailed_results (list): List of dictionaries containing detailed results for each polarization interval and pruning percentage.
    """
    # Save summary results
    if final_summary_results:
        df_final_summary = pd.DataFrame(final_summary_results)
        print("\n=== Final Summary Results ===")
        print(df_final_summary)
        summary_csv_path = 'data/results_summary.csv'
        df_final_summary.to_csv(summary_csv_path, index=False)
        print(f"\nSummary results saved to {summary_csv_path}")
    else:
        print("\nNo summary results to save.")

    # Save detailed results
    if detailed_results:
        df_detailed = pd.DataFrame(detailed_results)
        print("\n=== Detailed Results ===")
        print(df_detailed)
        detailed_csv_path = 'data/detailed_results.csv'
        df_detailed.to_csv(detailed_csv_path, index=False)
        print(f"\nDetailed results saved to {detailed_csv_path}")
    else:
        print("\nNo detailed results to save.")

    print("\nProcessing completed successfully.")