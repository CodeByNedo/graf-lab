from graf_lab_api.models.graph import Graph


def search_graph(graph: Graph, query: str) -> Graph:
    """Return the subgraph matching node attribute names or values.

    Matching is case-insensitive. Blank queries include every node.
    The result shares node and edge objects with the input graph.
    """
    query = query.casefold() if query.strip() else ""
    result = Graph(directed=graph.directed)

    for node in graph.nodes_view.values():
        if not query or any(
            query in name.casefold() or query in str(value).casefold()
            for name, value in node.attributes_view.items()
        ):
            result.add_node(node)

    for edge in graph.edges_view.values():
        if (
            edge.source in result.nodes_view
            and edge.target in result.nodes_view
        ):
            result.add_edge(edge)

    return result
