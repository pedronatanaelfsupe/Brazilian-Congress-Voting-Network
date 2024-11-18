import networkx as nx

def disparity_filter(G, alpha=0.01, min_giant_component_ratio=0.8, target_edge_ratio=0.1, max_alpha=1.0):
    """
    Apply the disparity filter to extract the backbone of a network,
    adjusting alpha to reduce the number of edges.

    Parameters:
    - G: NetworkX weighted graph.
    - alpha: initial level of significance for the disparity filter.
    - min_giant_component_ratio: minimum proportion of nodes in the giant component.
    - target_edge_ratio: target edge ratio in relation to the original graph.
    - max_alpha: maximum limit for the alpha value.

    Return:
    - G_backbone: resulting graph after applying the disparity filter.
    """
    def calculate_alpha_ij(k_i, p_ij):
        return 1 - (1 - p_ij)**(k_i - 1)

    # Sets the target number of edges in the backbone as a proportion of the original graph
    target_edges = int(G.number_of_edges() * target_edge_ratio)
    print(f"\n[INFO] Total number of nodes: {G.number_of_nodes()}, Total number of edges: {G.number_of_edges()}, Target edges for backbone: {target_edges}")

    while alpha <= max_alpha:
        G_backbone = nx.Graph()
        
        for node in G.nodes():
            neighbors = list(G[node])
            k_i = len(neighbors)
            sum_w = sum(G[node][neighbor]['weight'] for neighbor in neighbors)
            
            for neighbor in neighbors:
                w_ij = G[node][neighbor]['weight']
                p_ij = w_ij / sum_w
                alpha_ij = calculate_alpha_ij(k_i, p_ij)

                if alpha_ij <= alpha:
                    G_backbone.add_edge(node, neighbor, weight=w_ij)

        # If the G_backbone is empty, increase the alpha and continue
        if G_backbone.number_of_edges() == 0:
            print(f"[WARNING] G_backbone is empty with alpha={alpha:.2f}. Increasing alpha.")
            alpha += 0.005
            continue

        # Calculates the giant component and checks the proportion
        components = list(nx.connected_components(G_backbone))
        largest_component = max(components, key=len)
        giant_component_ratio = len(largest_component) / G.number_of_nodes()
        num_edges = G_backbone.number_of_edges()
        num_components = len(components)

        print(f"[DEBUG] Alpha={alpha:.2f} | Edges in the backbone: {num_edges} | Giant component ratio: {giant_component_ratio:.2f} | Number of components: {num_components}")

        # Stopping condition: giant component satisfies the minimum and number of edges is at the limit
        if giant_component_ratio >= min_giant_component_ratio and num_edges <= target_edges:
            print(f"[INFO] Conditions met: Final alpha={alpha:.2f}, Backbone edges={num_edges}, Giant component ratio={giant_component_ratio:.2f}")
            break
        elif alpha >= max_alpha:
            print(f"[INFO] Alpha limit reached ({max_alpha}). Stopping adjustment.")
            break
        else:
            # Aumenta alpha para ser mais permissivo e imprime o estado atual
            alpha += 0.005
            print(f"[INFO] Setting alpha to {alpha:.2f}. Current edges: {num_edges}, Giant component ratio: {giant_component_ratio:.2f}")

    return G_backbone