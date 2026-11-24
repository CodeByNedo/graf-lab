import re
import operator
from datetime import date
from graf_lab_api.models.graph import Graph

_OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


def _parse_filter(query: str) -> tuple[str, str, str]:
    """Parse a filter query into attribute, operator and value."""

    match = re.fullmatch(
        r"\s*(\S+)\s+(==|!=|>=|<=|>|<)\s+(.+?)\s*",
        query,
    )

    if match is None:
        raise ValueError("Invalid filter query")

    attribute, operator, value = match.groups()

    if value.startswith((">", "<", "=", "!")):
        raise ValueError("Invalid filter operator")

    return attribute, operator, value

def _compare_values(actual: int | float | str | date,
                    comparison: str,
                    expected: str) -> bool:
    """Compare an attribute value with a typed filter value."""

    if type(actual) in (int, float):
        try:
            expected_value = int(expected)
        except ValueError:
            try:
                expected_value = float(expected)
            except ValueError:
                raise ValueError(
                    f"Invalid numeric value: '{expected}'"
                ) from None

    elif type(actual) is date:
        try:
            expected_value = date.fromisoformat(expected)
        except ValueError:
            raise ValueError(
                f"Invalid date value: '{expected}'. Expected YYYY-MM-DD"
            ) from None

    else:
        expected_value = expected.strip().casefold()
        actual = actual.strip().casefold()

    return _OPERATORS[comparison](actual, expected_value)

def _attribute_type(value: int | float | str | date) -> str:
    """Return the attribute type category."""

    if type(value) in (int, float):
        return "numeric"

    return type(value).__name__

def filter_graph(graph: Graph, query: str) -> Graph:
    """Return a subgraph containing nodes matching the attribute filter."""

    result = Graph(directed=graph.directed)

    if not query.strip():
        matching_nodes = list(graph.nodes_view.values())
    else:
        attribute, comparison, expected = _parse_filter(query)

        attribute_types = {
            _attribute_type(node.attributes_view[attribute])
            for node in graph.nodes_view.values()
            if attribute in node.attributes_view
        }

        if len(attribute_types) > 1:
            raise ValueError(
                f"Incompatible types for attribute '{attribute}': "
                f"{', '.join(sorted(attribute_types))}"
            )

        matching_nodes = [
            node
            for node in graph.nodes_view.values()
            if attribute in node.attributes_view
            and _compare_values(
                node.attributes_view[attribute],
                comparison,
                expected,
            )
        ]

    for node in matching_nodes:
        result.add_node(node)

    for edge in graph.edges_view.values():
        if (
            edge.source in result.nodes_view
            and edge.target in result.nodes_view
        ):
            result.add_edge(edge)

    return result