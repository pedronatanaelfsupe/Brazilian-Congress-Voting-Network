import networkx as nx
import os
import pandas as pd
import matplotlib.pyplot as plt

def load_graphs(graphs_dir='data/graphs'):
    """
    Loads the .gml files of the graphs over the years.
    """
    graphs = {}
    for file in os.listdir(graphs_dir):
        if file.endswith('.gml'):
            year = int(file.split('_')[1])
            G = nx.read_gml(os.path.join(graphs_dir, file))
            graphs[year] = G
    return graphs

def get_party_info_by_community(G):
    """
    Extracts the number of deputies per party in each community into a graph G.
    """
    party_community_data = []
    for node, data in G.nodes(data=True):
        partido = data.get('sigla_partido', 'Unknown')
        comunidade = data.get('community', -1)
        party_community_data.append({'sigla_partido': partido, 'community': comunidade})
    
    df = pd.DataFrame(party_community_data)
    party_count_by_community = df.groupby(['sigla_partido', 'community']).size().reset_index(name='count')
    
    return party_count_by_community

def get_party_percentages_by_year(graphs):
    """
    Generates a table with the number and % of deputies from each party in each community over the years.
    """
    all_years_data = []
    
    for year, G in graphs.items():
        party_data = get_party_info_by_community(G)
        
        # Calcular o total de deputados por partido em cada ano
        total_deputados_by_party = party_data.groupby('sigla_partido')['count'].sum().reset_index(name='total')
        
        # Merge para calcular percentuais
        party_data = party_data.merge(total_deputados_by_party, on='sigla_partido')
        party_data['percentual'] = (party_data['count'] / party_data['total']) * 100
        party_data['year'] = year
        all_years_data.append(party_data)
    
    return pd.concat(all_years_data)

def export_party_community_table(party_data_by_year, output_file='data/party_community_table.csv'):
    """
    Exports a table that lists the parties and the number of deputies in each community per year,
    organized from largest to smallest party.
    
    Args:
        party_data_by_year (pd.DataFrame): DataFrame with party and community data over the years.
        output_file (str): Path to save the exported table.
    """
    # Group the data by party, year and community, and count the number of deputies
    grouped_data = party_data_by_year.groupby(['sigla_partido', 'year', 'community']).agg({'count': 'sum'}).reset_index()

    # Create a pivot table with years and communities in the columns
    pivot_table = grouped_data.pivot_table(index='sigla_partido', columns=['year', 'community'], values='count', fill_value=0)

    # Order parties from largest to smallest based on the total number of deputies over the years
    pivot_table['total_deputados'] = pivot_table.sum(axis=1)
    pivot_table = pivot_table.sort_values(by='total_deputados', ascending=False)

    # Remove the auxiliary column "total_deputados"
    pivot_table = pivot_table.drop(columns='total_deputados')

    # Export the table to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    pivot_table.to_csv(output_file)
    
    print(f"Party community table exported to {output_file}")

