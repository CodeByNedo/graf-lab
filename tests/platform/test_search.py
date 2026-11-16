from datetime import date

import pytest

from graf_lab_api.models.edge import Edge
from graf_lab_api.models.graph import Graph
from graf_lab_api.models.node import Node
from graf_lab_core.search import search_graph


@pytest.fixture(params=[True, False], ids=["directed", "undirected"])
def graph(request):
    graph = Graph(directed=request.param)
    graph.add_node(Node(id="A", attributes={"name": "Marko", "city": "Novi Sad"}))
    graph.add_node(Node(id="B", attributes={"name": "Ana", "city": "Novi Sad"}))
    graph.add_node(Node(id="C", attributes={"name": "Petar", "city": "Beograd"}))
    graph.add_node(Node(id="D"))
    graph.add_edge(Edge(id="AB", source="A", target="B", attributes={"weight": 5}))
    graph.add_edge(Edge(id="BA", source="B", target="A"))
    graph.add_edge(Edge(id="AC", source="A", target="C"))
    graph.add_edge(Edge(id="CB", source="C", target="B"))
    graph.add_edge(Edge(id="CC", source="C", target="C"))
    graph.add_edge(Edge(id="AA", source="A", target="A"))
    graph.add_edge(Edge(id="AB2", source="A", target="B"))
    return graph


@pytest.mark.parametrize("query", ["name", "NAM", "NaMe"])
def test_search_matches_attribute_names(graph, query):
    result = search_graph(graph, query)

    assert set(result.nodes_view) == {"A", "B", "C"}


@pytest.mark.parametrize("query", ["Marko", "ARK", "mAr"])
def test_search_matches_attribute_values(graph, query):
    result = search_graph(graph, query)

    assert set(result.nodes_view) == {"A"}


@pytest.mark.parametrize(
    "value, query",
    [
        (12345, "234"),
        (-42, "-4"),
        (9.75, ".7"),
        (date(2026, 11, 8), "2026-11-08"),
        (date(2026, 11, 8), "11-08"),
    ]
)
def test_search_matches_numeric_and_date_values(value, query):
    graph = Graph()
    graph.add_node(Node(id="A", attributes={"value": value}))
    graph.add_node(Node(id="B", attributes={"value": "other"}))

    result = search_graph(graph, query)

    assert set(result.nodes_view) == {"A"}


def test_search_uses_unicode_case_insensitive_matching():
    graph = Graph()
    graph.add_node(Node(id="A", attributes={"IME": "Čedomir"}))

    result = search_graph(graph, "čED")

    assert set(result.nodes_view) == {"A"}


def test_search_preserves_only_edges_between_matching_nodes(graph):
    result = search_graph(graph, "Novi")

    assert set(result.nodes_view) == {"A", "B"}
    assert set(result.edges_view) == {"AB", "BA", "AA", "AB2"}
    assert result.directed is graph.directed
    assert result.get_edge("AB").source == "A"
    assert result.get_edge("AB").target == "B"
    assert dict(result.get_edge("AB").attributes_view) == {"weight": 5}


def test_search_without_matches_returns_new_empty_graph(graph):
    result = search_graph(graph, "missing")

    assert result is not graph
    assert not result.nodes_view
    assert not result.edges_view
    assert result.directed is graph.directed


@pytest.mark.parametrize("query", ["", " ", " \t\n "])
def test_blank_search_returns_new_graph_with_all_nodes_and_edges(graph, query):
    result = search_graph(graph, query)

    assert result is not graph
    assert dict(result.nodes_view) == dict(graph.nodes_view)
    assert dict(result.edges_view) == dict(graph.edges_view)
    assert result.directed is graph.directed


@pytest.mark.parametrize("directed", [True, False])
@pytest.mark.parametrize("query", ["", " \t", "name"])
def test_search_empty_graph(directed, query):
    graph = Graph(directed=directed)

    result = search_graph(graph, query)

    assert result is not graph
    assert not result.nodes_view
    assert not result.edges_view
    assert result.directed is directed


@pytest.mark.parametrize("query", ["Novi", "missing", ""])
def test_search_does_not_modify_input_graph(graph, query):
    nodes = dict(graph.nodes_view)
    edges = dict(graph.edges_view)
    node_attributes = {
        node.id: dict(node.attributes_view) for node in graph.nodes_view.values()
    }
    edge_attributes = {
        edge.id: dict(edge.attributes_view) for edge in graph.edges_view.values()
    }
    directed = graph.directed

    result = search_graph(graph, query)

    assert result is not graph
    assert dict(graph.nodes_view) == nodes
    assert dict(graph.edges_view) == edges
    assert graph.directed is directed
    for node in graph.nodes_view.values():
        assert dict(node.attributes_view) == node_attributes[node.id]
    for edge in graph.edges_view.values():
        assert dict(edge.attributes_view) == edge_attributes[edge.id]


def test_result_has_independent_graph_structure(graph):
    result = search_graph(graph, "")

    result.remove_edge("AB")
    result.remove_node("D")
    result.add_node(Node(id="E"))

    assert "AB" in graph.edges_view
    assert "D" in graph.nodes_view
    assert "E" not in graph.nodes_view


def test_successive_searches_only_search_current_graph(graph):
    first = search_graph(graph, "Novi")
    second = search_graph(first, "Ana")
    empty = search_graph(first, "Petar")
    blank = search_graph(second, " ")

    assert set(first.nodes_view) == {"A", "B"}
    assert set(first.edges_view) == {"AB", "BA", "AA", "AB2"}
    assert set(second.nodes_view) == {"B"}
    assert not second.edges_view
    assert not empty.nodes_view
    assert not empty.edges_view
    assert set(blank.nodes_view) == {"B"}
    assert blank is not second
    assert blank.directed is graph.directed


def test_search_does_not_match_ids_or_edge_attributes():
    graph = Graph()
    graph.add_node(Node(id="needle"))
    graph.add_node(Node(id="B", attributes={"name": "other"}))
    graph.add_edge(Edge(
        id="needle_edge",
        source="needle",
        target="B",
        attributes={"needle": "needle"}
    ))

    result = search_graph(graph, "needle")

    assert not result.nodes_view
    assert not result.edges_view


def test_nonblank_query_preserves_spaces():
    graph = Graph()
    graph.add_node(Node(id="A", attributes={"name": "Novi Sad"}))
    graph.add_node(Node(id="B", attributes={"name": "NoviSad"}))

    result = search_graph(graph, "i S")

    assert set(result.nodes_view) == {"A"}
