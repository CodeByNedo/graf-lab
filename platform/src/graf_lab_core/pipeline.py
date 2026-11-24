"""Load, query and render graphs through plugins."""

from collections.abc import Mapping

from graf_lab_api.plugins import DataSourcePlugin, VisualizerPlugin

from .filter import filter_graph
from .search import search_graph


def render_graph(
    source: DataSourcePlugin,
    visualizer: VisualizerPlugin,
    parameters: Mapping[str, str],
    query: str | None = None,
    filter_query: str | None = None,
) -> str:
    """Load a graph, apply search then filter if supplied, and return HTML."""
    graph = source.load(parameters)

    if query is not None:
        graph = search_graph(graph, query)

    if filter_query is not None:
        graph = filter_graph(graph, filter_query)

    return visualizer.render(graph)
