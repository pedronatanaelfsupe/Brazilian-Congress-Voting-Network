import networkx as nx
import igraph as ig
import leidenalg
import matplotlib.pyplot as plt

def prune_graph(G, pruning_percentage):
    """
    Prunes the graph by removing edges below a certain normalized weight threshold.

    Args:
        G (nx.Graph): The original graph.
        pruning_percentage (float): The percentage threshold for pruning.

    Returns:
        nx.Graph: The pruned graph.
    """
    threshold = pruning_percentage / 100.0
    edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d['normalized_weight'] < threshold]
    G.remove_edges_from(edges_to_remove)

    # Ensure no node is isolated
    for node in list(G.nodes()):
        if G.degree(node) == 0:
            # Find the strongest edge to reconnect
            edges = [(u, v, d) for u, v, d in G.edges(node, data=True)]
            if edges:
                max_edge = max(edges, key=lambda x: x[2]['normalized_weight'])
                G.add_edge(*max_edge[:2], **max_edge[2])

    return G

def detect_communities(G, random_state=None):
    """
    Detects communities in the graph using the Leiden algorithm.

    Args:
        G (nx.Graph): The graph.
        random_state (int, optional): Seed for the random number generator.

    Returns:
        tuple: A tuple containing the community mapping and modularity.
    """
    # Convert NetworkX graph to iGraph
    ig_graph = ig.Graph.from_networkx(G)
    partition = leidenalg.find_partition(
        ig_graph,
        leidenalg.ModularityVertexPartition,
        seed=random_state
    )
    modularity = partition.modularity

    # Map community labels back to NetworkX nodes
    communities = {
        node: membership for node, membership in zip(G.nodes(), partition.membership)
    }

    return communities, modularity


def analyze_pruning(G, pruning_percentages, random_state=None):
    """
    Analyzes the effect of pruning on community detection.

    Args:
        G (nx.Graph): The original graph.
        pruning_percentages (list): A list of pruning percentages.
        random_state (int, optional): Seed for the random number generator.

    Returns:
        list: A list of dictionaries containing the results for each pruning percentage.
    """
    results = []
    for p in pruning_percentages:
        G_pruned = prune_graph(G.copy(), p)
        communities, modularity = detect_communities(G_pruned, random_state=random_state)
        num_communities = len(set(communities.values()))
        results.append({
            'pruning_percentage': p,
            'num_communities': num_communities,
            'modularity': modularity
        })
        print(f"Pruning at {p}%: {num_communities} communities, modularity={modularity:.4f}")
    return results

def plot_results(results):
    """
    Plots the number of communities and modularity against pruning percentages.

    Args:
        results (list): The results from the pruning analysis.
    """
    pruning_percentages = [res['pruning_percentage'] for res in results]
    num_communities = [res['num_communities'] for res in results]
    modularities = [res['modularity'] for res in results]

    # Plot number of communities
    plt.figure(figsize=(10, 5))
    plt.plot(pruning_percentages, num_communities, marker='o')
    plt.title('Number of Communities vs Pruning Percentage')
    plt.xlabel('Pruning Percentage (%)')
    plt.ylabel('Number of Communities')
    plt.grid(True)
    plt.show()

    # Plot modularity
    plt.figure(figsize=(10, 5))
    plt.plot(pruning_percentages, modularities, marker='o', color='orange')
    plt.title('Modularity vs Pruning Percentage')
    plt.xlabel('Pruning Percentage (%)')
    plt.ylabel('Modularity')
    plt.grid(True)
    plt.show()
