from datetime import date

import pytest

from graf_lab_api.models import Node, Edge, Graph
from graf_lab_core.filter import _parse_filter, _compare_values, filter_graph
from graf_lab_core.search import search_graph


@pytest.mark.parametrize(
    "query, expected",
    [
        ("age >= 20", ("age", ">=", "20")),
        ("height < 1.85", ("height", "<", "1.85")),
        ("city == Novi Sad", ("city", "==", "Novi Sad")),
        ("age != 30", ("age", "!=", "30")),
        ("age <= 25", ("age", "<=", "25")),
        ("age > 18", ("age", ">", "18")),
    ],
)
def test_parse_valid_filter(query, expected):
    assert _parse_filter(query) == expected


@pytest.mark.parametrize(
    "query",
    [
        "age 20",
        "age >",
        "age >> 20",
        "age",
    ],
)
def test_parse_invalid_filter(query):
    with pytest.raises(ValueError):
        _parse_filter(query)


@pytest.mark.parametrize(
    "actual, comparison, expected, result",
    [
        # Integer and float comparisons
        (25, ">", "20", True),
        (25, "<", "20", False),
        (25, "==", "25", True),
        (25, "!=", "30", True),
        (25, ">=", "25.0", True),
        (1.85, "<=", "1.90", True),
        (1.85, ">", "2", False),
        (9007199254740993, "==", "9007199254740992", False),

        # Case-insensitive string comparisons
        ("Marko", "==", "marko", True),
        ("NOVI SAD", "==", "novi sad", True),
        ("Marko", "!=", "Petar", True),
        (" Ana ", "==", "ana", True),

        # Date comparisons
        (date(2026, 11, 16), "<", "2026-12-01", True),
        (date(2026, 11, 16), ">", "2026-12-01", False),
        (date(2026, 11, 16), "==", "2026-11-16", True),
    ],
)
def test_compare_values(actual, comparison, expected, result):
    assert _compare_values(actual, comparison, expected) is result


@pytest.mark.parametrize(
    "actual, comparison, expected",
    [
        (25, ">", "abc"),
        (1.85, "<", "hello"),
        (date(2026, 11, 16), "==", "invalid-date"),
        (date(2026, 11, 16), ">", "2026-13-01"),
    ],
)
def test_compare_invalid_values(actual, comparison, expected):
    with pytest.raises(ValueError):
        _compare_values(actual, comparison, expected)

def test_filter_graph_returns_matching_subgraph():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 18}))
    graph.add_node(Node(id="2", attributes={"age": 25}))
    graph.add_node(Node(id="3", attributes={"age": 30}))

    graph.add_edge(Edge(id="e1", source="1", target="2"))
    graph.add_edge(Edge(id="e2", source="2", target="3"))

    result = filter_graph(graph, "age > 20")

    assert set(result.nodes_view) == {"2", "3"}
    assert set(result.edges_view) == {"e2"}

    # Originalni graf mora ostati nepromijenjen.
    assert len(graph.nodes_view) == 3
    assert len(graph.edges_view) == 2

def test_filter_graph_excludes_nodes_without_attribute():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 25}))
    graph.add_node(Node(id="2", attributes={"name": "Marko"}))
    graph.add_node(Node(id="3", attributes={"age": 30}))

    result = filter_graph(graph, "age > 20")

    assert set(result.nodes_view) == {"1", "3"}


def test_filter_graph_returns_empty_when_attribute_missing():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 25}))
    graph.add_node(Node(id="2", attributes={"age": 30}))

    result = filter_graph(graph, "salary > 1000")

    assert len(result.nodes_view) == 0
    assert len(result.edges_view) == 0


def test_filter_graph_blank_query_keeps_current_graph():
    graph = Graph(directed=False)

    graph.add_node(Node(id="1", attributes={"age": 25}))
    graph.add_node(Node(id="2", attributes={"age": 30}))
    graph.add_edge(Edge(id="e1", source="1", target="2"))

    result = filter_graph(graph, "   ")

    assert result is not graph
    assert result.directed is False
    assert set(result.nodes_view) == {"1", "2"}
    assert set(result.edges_view) == {"e1"}

def test_filter_graph_rejects_incompatible_attribute_types():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 25}))
    graph.add_node(Node(id="2", attributes={"age": 30.5}))
    graph.add_node(Node(id="3", attributes={"age": "unknown"}))

    with pytest.raises(ValueError):
        filter_graph(graph, "age > 20")

    # Originalni graf mora ostati nepromijenjen.
    assert set(graph.nodes_view) == {"1", "2", "3"}

def test_filter_then_search():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"name": "Marko", "age": 18}))
    graph.add_node(Node(id="2", attributes={"name": "Ana", "age": 25}))
    graph.add_node(Node(id="3", attributes={"name": "Anastasija", "age": 30}))
    graph.add_node(Node(id="4", attributes={"name": "Petar", "age": 35}))

    graph.add_edge(Edge(id="e1", source="1", target="2"))
    graph.add_edge(Edge(id="e2", source="2", target="3"))
    graph.add_edge(Edge(id="e3", source="3", target="4"))

    filtered = filter_graph(graph, "age > 20")
    searched = search_graph(filtered, "ana")

    assert set(filtered.nodes_view) == {"2", "3", "4"}
    assert set(filtered.edges_view) == {"e2", "e3"}

    assert set(searched.nodes_view) == {"2", "3"}
    assert set(searched.edges_view) == {"e2"}

    assert len(graph.nodes_view) == 4
    assert len(graph.edges_view) == 3

def test_search_then_filter():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"name": "Ana", "age": 18}))
    graph.add_node(Node(id="2", attributes={"name": "Anastasija", "age": 25}))
    graph.add_node(Node(id="3", attributes={"name": "Marko", "age": 30}))

    graph.add_edge(Edge(id="e1", source="1", target="2"))
    graph.add_edge(Edge(id="e2", source="2", target="3"))

    searched = search_graph(graph, "ana")
    filtered = filter_graph(searched, "age > 20")

    assert set(searched.nodes_view) == {"1", "2"}
    assert set(searched.edges_view) == {"e1"}

    assert set(filtered.nodes_view) == {"2"}
    assert len(filtered.edges_view) == 0

    assert len(graph.nodes_view) == 3

def test_multiple_successive_filters():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 18}))
    graph.add_node(Node(id="2", attributes={"age": 25}))
    graph.add_node(Node(id="3", attributes={"age": 30}))
    graph.add_node(Node(id="4", attributes={"age": 40}))

    graph.add_edge(Edge(id="e1", source="1", target="2"))
    graph.add_edge(Edge(id="e2", source="2", target="3"))
    graph.add_edge(Edge(id="e3", source="3", target="4"))

    first_filter = filter_graph(graph, "age >= 20")
    second_filter = filter_graph(first_filter, "age < 35")

    assert set(first_filter.nodes_view) == {"2", "3", "4"}
    assert set(first_filter.edges_view) == {"e2", "e3"}

    assert set(second_filter.nodes_view) == {"2", "3"}
    assert set(second_filter.edges_view) == {"e2"}

    assert len(graph.nodes_view) == 4

def test_filter_graph_rejects_invalid_numeric_value():
    graph = Graph()
    graph.add_node(Node(id="1", attributes={"age": 25}))

    with pytest.raises(ValueError):
        filter_graph(graph, "age > unknown")


def test_filter_graph_rejects_invalid_date_value():
    graph = Graph()
    graph.add_node(
        Node(id="1", attributes={"created": date(2026, 11, 10)})
    )

    with pytest.raises(ValueError):
        filter_graph(graph, "created >= invalid")


def test_filter_graph_preserves_large_integer_precision():
    graph = Graph()

    graph.add_node(Node(
        id="1",
        attributes={"number": 9007199254740992}
    ))

    result = filter_graph(
        graph,
        "number == 9007199254740993"
    )

    assert len(result.nodes_view) == 0


def test_filter_graph_missing_attribute_with_invalid_value():
    graph = Graph()

    graph.add_node(Node(id="1", attributes={"age": 25}))
    graph.add_node(Node(id="2", attributes={"age": 30}))

    result = filter_graph(graph, "salary > unknown")

    assert len(result.nodes_view) == 0
    assert len(result.edges_view) == 0