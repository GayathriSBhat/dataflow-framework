# routing_engine/visualize.py
import math
import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(engine, show=True, filename=None, figsize=(10, 6)):
    """
    Draw the engine.graph with edge widths proportional to transition counts.

    - engine: RoutingEngine instance
    - show: whether to call plt.show()
    - filename: if provided, save the figure to this path
    """
    G = engine.graph
    if G.number_of_nodes() == 0:
        raise ValueError("Graph is empty. Run the engine first or register nodes.")

    plt.figure(figsize=figsize)
    pos = nx.spring_layout(G, seed=42)  # deterministic layout

    # Nodes: make 'start' and 'end' visually distinct
    node_colors = []
    node_sizes = []
    for n in G.nodes():
        if n == "start":
            node_colors.append("#a1d99b")  # light green
            node_sizes.append(1400)
        elif n == "end":
            node_colors.append("#fc9272")  # light red
            node_sizes.append(1400)
        else:
            node_colors.append("#9ecae1")  # light blue
            node_sizes.append(1000)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, edgecolors="k")
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

    # Prepare edge widths from counts (default to 1)
    edge_counts = []
    labels = {}
    max_count = 0
    for u, v, data in G.edges(data=True):
        c = data.get("count", 1)
        edge_counts.append(c)
        labels[(u, v)] = str(c)
        if c > max_count:
            max_count = c

    # normalize widths for display (scale sqrt to reduce skew)
    widths = []
    if max_count == 0:
        widths = [1.0 for _ in edge_counts]
    else:
        for c in edge_counts:
            widths.append(1.0 + math.sqrt(c))  # visual scaling

    nx.draw_networkx_edges(G, pos, width=widths, arrowsize=20, arrowstyle='-|>')
    # draw edge labels (counts)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color="gray", font_size=9)

    plt.title("Routing Engine Graph (edge labels = transition counts)")
    plt.axis("off")
    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=200)
        print(f"Saved graph image to: {filename}")

    if show:
        plt.show()

    plt.close()
