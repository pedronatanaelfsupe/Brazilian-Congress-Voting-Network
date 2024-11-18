import pandas as pd
import networkx as nx
import numpy as np
from networkx.readwrite.gpickle import write_gpickle

def generate_graph(df_votes, year):
    """
    Generates a graph for a given year based on voting data.

    Args:
        df_votes (pd.DataFrame): The DataFrame containing voting data.
        year (int): The year for which to generate the graph.

    Returns:
        nx.Graph: The generated graph.
    """
    # Filter votes for the specified year
    df_year = df_votes[df_votes['ano_votacao'] == year]

    # Keep only 'Sim' and 'Não' votes
    df_year = df_year[df_year['voto'].isin(['Sim', 'Não'])]

    # Create a pivot table with deputies as rows and votacoes as columns
    pivot_table = df_year.pivot_table(index='id_deputado', columns='id_votacao', values='voto', aggfunc='first')

    # Map votes to numerical values
    vote_mapping = {'Sim': 1, 'Não': -1}
    pivot_table = pivot_table.replace(vote_mapping).fillna(0)

    # Calculate the adjacency matrix
    adjacency_matrix = pivot_table.dot(pivot_table.T)

    # Create the graph from the adjacency matrix
    G = nx.from_numpy_array(adjacency_matrix.values)
    mapping = dict(enumerate(pivot_table.index))
    G = nx.relabel_nodes(G, mapping)

    # Normalize edge weights
    weights = [data['weight'] for _, _, data in G.edges(data=True)]
    min_weight = min(weights)
    max_weight = max(weights)
    for u, v, data in G.edges(data=True):
        data['normalized_weight'] = (data['weight'] - min_weight) / (max_weight - min_weight)

    # Add node attributes (id_deputado)
    for node in G.nodes():
        G.nodes[node]['id_deputado'] = node

    return G

def convert_attributes(G):
    """
    Converts node and edge attributes to types compatible with GML format.

    Args:
        G (nx.Graph): The graph to process.

    Returns:
        nx.Graph: The graph with converted attributes.
    """
    for node, data in G.nodes(data=True):
        for attr, value in data.items():
            if isinstance(value, (list, dict, set)):
                # Convert complex data types to strings
                G.nodes[node][attr] = str(value)
            elif isinstance(value, np.integer):
                G.nodes[node][attr] = int(value)
            elif isinstance(value, np.floating):
                G.nodes[node][attr] = float(value)
            elif isinstance(value, np.bool_):
                G.nodes[node][attr] = bool(value)
            # Add additional type conversions if necessary

    for u, v, data in G.edges(data=True):
        for attr, value in data.items():
            if isinstance(value, (list, dict, set)):
                G.edges[u, v][attr] = str(value)
            elif isinstance(value, np.integer):
                G.edges[u, v][attr] = int(value)
            elif isinstance(value, np.floating):
                G.edges[u, v][attr] = float(value)
            elif isinstance(value, np.bool_):
                G.edges[u, v][attr] = bool(value)
            # Add additional type conversions if necessary

    return G

def save_graph(G, path):
    """
    Saves the graph to a GML file.

    Args:
        G (nx.Graph): The graph to save.
        path (str): The file path to save the graph to.
    """
    # Convert attributes to GML-compatible types
    G = convert_attributes(G)

    # Save the graph in GML format
    nx.write_gml(G, path, stringizer=str)
    print(f"Graph saved to {path}")
