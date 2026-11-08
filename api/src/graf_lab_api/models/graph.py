
from types import MappingProxyType
from typing import Mapping

from .node import Node
from .edge import Edge


class Graph:
    """Represents a directed or undirected graph of nodes and edges."""

    def __init__(self, directed: bool = True):
        """Initialize an empty graph with the specified directionality."""

        if not isinstance(directed, bool):
            raise ValueError("Graph directed must be a boolean")

        self._directed = directed
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, Edge] = {}

    @property
    def directed(self) -> bool:
        """Return whether the graph is directed."""
        return self._directed

    @property
    def nodes_view(self) -> Mapping[str, Node]:
        """Return a read-only view of nodes indexed by ID."""
        return MappingProxyType(self._nodes)

    @property
    def edges_view(self) -> Mapping[str, Edge]:
        """Return a read-only view of edges indexed by ID."""
        return MappingProxyType(self._edges)

    def add_node(self, node: Node) -> None:
        """Add a node, rejecting duplicate IDs."""

        if not isinstance(node, Node):
            raise ValueError("Graph accepts only Node objects")

        if node.id in self._nodes:
            raise ValueError(f"Duplicate node ID: '{node.id}'")

        self._nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        """Add an edge if its ID is unique and both endpoints exist."""

        if not isinstance(edge, Edge):
            raise ValueError("Graph accepts only Edge objects")

        if edge.id in self._edges:
            raise ValueError(f"Duplicate edge ID: '{edge.id}'")

        if edge.source not in self._nodes:
            raise ValueError(
                f"Source node '{edge.source}' does not exist"
            )

        if edge.target not in self._nodes:
            raise ValueError(
                f"Target node '{edge.target}' does not exist"
            )

        self._edges[edge.id] = edge

    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge by ID."""

        if edge_id not in self._edges:
            raise ValueError(f"Edge '{edge_id}' does not exist")

        del self._edges[edge_id]

    def remove_node(self, node_id: str) -> None:
        """Remove a node only if it has no connected edges."""

        if node_id not in self._nodes:
            raise ValueError(f"Node '{node_id}' does not exist")

        for edge in self._edges.values():
            if edge.source == node_id or edge.target == node_id:
                raise ValueError(
                    f"Cannot remove node '{node_id}': "
                    "node has connected edges"
                )

        del self._nodes[node_id]

    def get_node(self, node_id: str) -> Node:
        """Return a node by ID, raising ValueError if it does not exist."""

        if node_id not in self._nodes:
            raise ValueError(f"Node '{node_id}' does not exist")

        return self._nodes[node_id]

    def get_edge(self, edge_id: str) -> Edge:
        """Return an edge by ID, raising ValueError if it does not exist."""

        if edge_id not in self._edges:
            raise ValueError(f"Edge '{edge_id}' does not exist")

        return self._edges[edge_id]
