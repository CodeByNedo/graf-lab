"""Contracts for plugins used by the Graf Lab platform."""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from .models import Graph


class DataSourcePlugin(ABC):
    """Load graph data from a source supported by the plugin."""

    @abstractmethod
    def load(self, parameters: Mapping[str, str]) -> Graph:
        """Read the source using plugin-specific parameters and return its graph."""
        raise NotImplementedError


class VisualizerPlugin(ABC):
    """Convert a graph to content that the web application can display."""

    @abstractmethod
    def render(self, graph: Graph) -> str:
        """Return the HTML representation of the supplied graph."""
        raise NotImplementedError
