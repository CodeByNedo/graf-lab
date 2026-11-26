from collections.abc import Mapping
from copy import deepcopy
from uuid import uuid4
from types import MappingProxyType

from graf_lab_api.models.graph import Graph
from graf_lab_api.plugins import DataSourcePlugin
from .search import search_graph
from .filter import filter_graph


class Workspace:
    """Represents an independent workspace for graph exploration."""

    def __init__(
        self,
        source: DataSourcePlugin,
        parameters: Mapping[str, str],
    ):
        self._id = str(uuid4())
        self._source = source
        self._parameters = dict(parameters)

        self._original_graph: Graph = deepcopy(
            source.load(self._parameters)
        )
        self._current_graph: Graph = deepcopy(
            self._original_graph
        )

        self._query_history: list[tuple[str, str]] = []

    @property
    def id(self) -> str:
        """Return the workspace ID."""
        return self._id

    @property
    def source(self) -> DataSourcePlugin:
        """Return the workspace data source."""
        return self._source

    @property
    def parameters(self) -> Mapping[str, str]:
        """Return a read-only view of source parameters."""
        return MappingProxyType(self._parameters)

    @property
    def original_graph(self) -> Graph:
        """Return an independent copy of the original graph."""
        return deepcopy(self._original_graph)

    @property
    def current_graph(self) -> Graph:
        """Return the current graph."""
        return self._current_graph

    @property
    def query_history(self) -> tuple[tuple[str, str], ...]:
        """Return applied queries in their execution order."""
        return tuple(self._query_history)
    
    def search(self, query: str) -> None:
        """Apply a search query to the current graph."""
        self._current_graph = search_graph(
            self._current_graph, query
        )
        self._query_history.append(("search", query))

    def filter(self, query: str) -> None:
        """Apply a filter query to the current graph."""
        self._current_graph = filter_graph(
            self._current_graph, query
        )
        self._query_history.append(("filter", query))

    def reset(self) -> None:
        """Restore the original graph and clear query history."""
        self._current_graph = deepcopy(self._original_graph)
        self._query_history.clear()