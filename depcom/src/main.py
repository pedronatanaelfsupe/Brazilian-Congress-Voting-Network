import pandas as pd
import numpy as np
import random
from utils import data_acquisition, data_processing, optimize_polarization_interval, save_results
from backbone import analyze_voting_network, data_processing_backbone
from D_temporal_consistency import (
    load_graphs, 
    get_party_percentages_by_year, 
    export_party_community_table, 
    clean_dataframe, 
    adjust_community_labels, 
    sort_columns, 
    get_last_year, 
    export_dataframe_to_csv,
    get_min_community_generalized,
    merge_min_community_with_suffix_change)

def main():
    # Set the fixed random state
    fixed_random_state = 42

    # Set random seeds
    random.seed(fixed_random_state)
    np.random.seed(fixed_random_state)

    # Step 1: Data Acquisition
    data_acquisition()

    #Prepare voting data
    df_votacao_parlamentar = pd.read_csv('data/csv/votacao_parlamentar.csv')

    # Prepare deputies information
    df_deputados = df_votacao_parlamentar[['id_deputado', 'nome', 'sigla_partido', 'sigla_uf']].drop_duplicates(subset='id_deputado')

    # Step 2: Data Pre-Processing
    df_filtered, num_propositions_before, df_orgao_deputado = data_processing()
    if df_filtered is None:
        print("Error in data processing. Ending the script.")
        return

    # Step 3: Optimize Polarization Interval and Perform Analysis
    final_summary_results, detailed_results = optimize_polarization_interval(df_filtered, df_deputados, fixed_random_state)

    #Save Final Results
    save_results(final_summary_results, detailed_results)

    # Step 4: Ensure Temporal Consistency of Communities
    
    graphs_dir = 'data/graphs'

    # Load Graphs
    graphs = load_graphs(graphs_dir)
    
    # Extract data from parties and communities over the years
    party_data_by_year = get_party_percentages_by_year(graphs)

    # Export the table with the number of deputies per party in each community over the years
    export_party_community_table(party_data_by_year, output_file='data/party_community_table.csv')

    df = clean_dataframe(pd.read_csv('data/party_community_table.csv'))

    df_min = get_min_community_generalized(df)

    # Specify the reference year
    reference_year = get_last_year(df)

    # Adjust community labels
    adjusted_df = adjust_community_labels(df, reference_year)

    adjusted_df = merge_min_community_with_suffix_change(adjusted_df, df_min)

    # Sort columns from the earliest year to the latest year
    sorted_df = sort_columns(adjusted_df)

    export_dataframe_to_csv(sorted_df, 'data/party_community_table_adjusted.csv')
    
    # Processes the data and displays the DataFrame
    df_votacao_parlamentar = data_processing_backbone()
    print("Data processing completed. Final DataFrame structure:")
    print(df_votacao_parlamentar.head())

    # Comparison with Backbone extraction method

    # Sets the range of years between 2004 and 2023
    years = range(2004, 2024)

    results = []

    for year in years:
        result = analyze_voting_network(df_votacao_parlamentar, year)
        if result is not None:
            results.append(result)

    # Save results to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv('data/results_backbone.csv', index=False)
    print("Resultados salvos em 'data/results_backbone.csv'.")

if __name__ == "__main__":
    main()