import pandas as pd
import networkx as nx
from C_modularity_optimization import disparity_filter  # Assumindo que há um módulo que implementa o filtro de disparidade
import igraph as ig
import leidenalg

def data_processing_backbone():
    """
    Carrega e processa o dataset `votacao_parlamentar`.
    
    Retorna:
        pd.DataFrame: DataFrame processado com a coluna 'ano_votacao' adicionada.
    """
    print("Iniciando o processamento de dados...")

    # Carrega o dataset
    df_votacao_parlamentar = pd.read_csv('data/csv/votacao_parlamentar.csv')
    print("Dados carregados. Primeiras linhas:")
    print(df_votacao_parlamentar.head())

    # Converte a coluna 'data' para datetime
    df_votacao_parlamentar['data'] = pd.to_datetime(df_votacao_parlamentar['data'], errors='coerce')
    print("Coluna 'data' convertida para datetime. Tipos de dados:")
    print(df_votacao_parlamentar.dtypes)

    # Extrai o ano da coluna 'data' e cria a coluna 'ano_votacao'
    df_votacao_parlamentar['ano_votacao'] = df_votacao_parlamentar['data'].dt.year
    print("Coluna 'ano_votacao' criada. Primeiras linhas com 'ano_votacao':")
    print(df_votacao_parlamentar[['data', 'ano_votacao']].head())

    # Retorna o DataFrame processado
    return df_votacao_parlamentar

def analyze_voting_network(df_votes, year):
    """
    Gera e analisa o grafo de votação para um ano específico.

    Args:
        df_votes (pd.DataFrame): DataFrame com as votações do ano.
        year (int): Ano sendo analisado.

    Retorna:
        dict: Resultados de modularidade e comunidades.
    """
    print(f"\nAnalisando o ano {year}...")
    # Filtra as votações para o ano atual
    df_votes_year = df_votes[df_votes['ano_votacao'] == year]
    print(f"Filtragem de dados para o ano {year} concluída. Número de registros: {len(df_votes_year)}")

    # Verifica se o DataFrame filtrado está vazio
    if df_votes_year.empty:
        print(f"Nenhuma votação encontrada para o ano {year}.")
        return None

    # Cria um grafo vazio
    G = nx.Graph()

    # Agrupa deputados por id_votacao e voto (Sim ou Não)
    for _, group in df_votes_year.groupby(['id_votacao', 'voto']):
        # Lista de deputados que votaram da mesma forma em uma proposição específica
        deputados = list(group['id_deputado'])

        # Conecta cada par de deputados que votou da mesma forma
        for i in range(len(deputados)):
            for j in range(i + 1, len(deputados)):
                if G.has_edge(deputados[i], deputados[j]):
                    G[deputados[i]][deputados[j]]['weight'] += 1
                else:
                    G.add_edge(deputados[i], deputados[j], weight=1)

    # Aplica o "backbone extraction"
    G_backbone = disparity_filter(G)
    print(f"Ano {year}: Número de arestas no G_backbone após disparity_filter = {G_backbone.number_of_edges()}")

    # Atribui o atributo 'name' para cada nó com o valor de 'id_deputado' no G_backbone
    for node in G_backbone.nodes():
        G_backbone.nodes[node]['name'] = node

    # Converter o grafo NetworkX para igraph e configurar os atributos de nó
    G_ig = ig.Graph.from_networkx(G_backbone)
    G_ig.vs['name'] = [v['name'] for v in G_backbone.nodes.values()]

    # Detectar comunidades usando o algoritmo Leiden
    partition = leidenalg.find_partition(G_ig, leidenalg.ModularityVertexPartition)
    modularity = partition.modularity

    # Extrair as comunidades e contar deputados por partido em cada comunidade
    communities = partition
    community_party_count = {}
    for i, community in enumerate(communities):
        party_count = {}
        for node in community:
            # 'node' é o índice do nó no grafo igraph
            node_id = G_ig.vs[node]['name']  # Obtém o ID original do nó
            
            # Verifica se o deputado existe no DataFrame antes de tentar acessar
            deputado_info = df_votes_year[df_votes_year['id_deputado'] == node_id]
            if not deputado_info.empty:
                party = deputado_info['sigla_partido'].values[0]
            else:
                party = 'Unknown'  # Valor padrão se o deputado não estiver no DataFrame
            
            party_count[party] = party_count.get(party, 0) + 1
        community_party_count[f'Community_{i+1}'] = party_count

    print(f"Ano {year}: Modularidade calculada = {modularity}, Número de comunidades = {len(communities)}")
    return {
        'Year': year,
        'Modularity': modularity,
        'Num_Communities': len(communities),
        'Community_Party_Count': community_party_count
    }