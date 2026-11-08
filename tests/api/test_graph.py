
import pytest

from graf_lab_api.models.node import Node
from graf_lab_api.models.graph import Graph
from graf_lab_api.models.edge import Edge


def test_graph_is_directed_by_default():
    graph = Graph()
    assert graph.directed is True


def test_graph_can_be_undirected():
    graph = Graph(directed=False)
    assert graph.directed is False


@pytest.mark.parametrize("invalid_directed", [None, 0, 1, "yes"])
def test_graph_rejects_invalid_directed(invalid_directed):
    with pytest.raises(ValueError):
        Graph(directed=invalid_directed)


def test_graph_starts_empty():
    graph = Graph()

    assert len(graph.nodes_view) == 0
    assert len(graph.edges_view) == 0


def test_graph_adds_node():
    graph = Graph()
    node = Node(id="A")

    graph.add_node(node)

    assert graph.nodes_view["A"] is node


def test_graph_adds_multiple_nodes():
    graph = Graph()

    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    assert len(graph.nodes_view) == 2
    assert "A" in graph.nodes_view
    assert "B" in graph.nodes_view


def test_graph_rejects_duplicate_node_id():
    graph = Graph()

    graph.add_node(Node(id="A", attributes={"name": "Marko"}))

    with pytest.raises(ValueError, match="Duplicate node ID"):
        graph.add_node(Node(id="A", attributes={"name": "Ana"}))

    assert len(graph.nodes_view) == 1


@pytest.mark.parametrize("invalid_node", [None, "A", 123, {}])
def test_graph_rejects_invalid_node(invalid_node):
    graph = Graph()

    with pytest.raises(ValueError):
        graph.add_node(invalid_node)


def test_graph_nodes_view_cannot_be_modified_directly():
    graph = Graph()

    with pytest.raises(TypeError):
        graph.nodes_view["A"] = Node(id="A")


def test_graph_edges_view_cannot_be_modified_directly():
    graph = Graph()

    with pytest.raises(TypeError):
        graph.edges_view["edge_1"] = "invalid"


def test_separate_graphs_can_use_same_node_id():
    graph1 = Graph()
    graph2 = Graph()

    graph1.add_node(Node(id="A"))
    graph2.add_node(Node(id="A"))

    assert len(graph1.nodes_view) == 1
    assert len(graph2.nodes_view) == 1


def test_graph_adds_edge():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    edge = Edge(source="A", target="B", id="edge_1")
    graph.add_edge(edge)

    assert graph.edges_view["edge_1"] is edge


def test_graph_rejects_duplicate_edge_id():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    graph.add_edge(Edge(source="A", target="B", id="edge_1"))

    with pytest.raises(ValueError, match="Duplicate edge ID"):
        graph.add_edge(Edge(source="B", target="A", id="edge_1"))

    assert len(graph.edges_view) == 1


def test_graph_rejects_missing_source():
    graph = Graph()
    graph.add_node(Node(id="B"))

    with pytest.raises(ValueError, match="Source node"):
        graph.add_edge(Edge(source="A", target="B"))

    assert len(graph.edges_view) == 0


def test_graph_rejects_missing_target():
    graph = Graph()
    graph.add_node(Node(id="A"))

    with pytest.raises(ValueError, match="Target node"):
        graph.add_edge(Edge(source="A", target="B"))

    assert len(graph.edges_view) == 0


@pytest.mark.parametrize("invalid_edge", [None, "edge", 123, {}])
def test_graph_rejects_invalid_edge(invalid_edge):
    graph = Graph()

    with pytest.raises(ValueError):
        graph.add_edge(invalid_edge)


def test_graph_allows_self_loop():
    graph = Graph()
    graph.add_node(Node(id="A"))

    edge = Edge(source="A", target="A")
    graph.add_edge(edge)

    assert len(graph.edges_view) == 1


def test_graph_allows_multiple_edges_between_same_nodes():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    graph.add_edge(Edge(source="A", target="B", id="edge_1"))
    graph.add_edge(Edge(source="A", target="B", id="edge_2"))

    assert len(graph.edges_view) == 2


def test_graph_adds_edge_with_attributes():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    edge = Edge(
        source="A",
        target="B",
        attributes={"weight": 5, "label": "poznaje"}
    )

    graph.add_edge(edge)

    assert graph.edges_view[edge.id].attributes_view["weight"] == 5


def test_graph_allows_reverse_edge_in_directed_graph():
    graph = Graph(directed=True)
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    graph.add_edge(Edge(source="A", target="B", id="edge_1"))
    graph.add_edge(Edge(source="B", target="A", id="edge_2"))

    assert len(graph.edges_view) == 2


def test_graph_removes_edge():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    graph.add_edge(Edge(source="A", target="B", id="e1"))

    graph.remove_edge("e1")

    assert len(graph.edges_view) == 0
    assert len(graph.nodes_view) == 2


def test_graph_rejects_removing_nonexistent_edge():
    graph = Graph()

    with pytest.raises(ValueError, match="does not exist"):
        graph.remove_edge("unknown")


def test_graph_removes_isolated_node():
    graph = Graph()
    graph.add_node(Node(id="A"))

    graph.remove_node("A")

    assert "A" not in graph.nodes_view


def test_graph_rejects_removing_nonexistent_node():
    graph = Graph()

    with pytest.raises(ValueError, match="does not exist"):
        graph.remove_node("unknown")


def test_graph_rejects_removing_connected_source_node():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_edge(Edge(source="A", target="B", id="e1"))

    with pytest.raises(ValueError, match="connected edges"):
        graph.remove_node("A")

    assert "A" in graph.nodes_view


def test_graph_rejects_removing_connected_target_node():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_edge(Edge(source="A", target="B", id="e1"))

    with pytest.raises(ValueError, match="connected edges"):
        graph.remove_node("B")

    assert "B" in graph.nodes_view


def test_graph_rejects_removing_node_with_self_loop():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_edge(Edge(source="A", target="A", id="e1"))

    with pytest.raises(ValueError, match="connected edges"):
        graph.remove_node("A")

    assert "A" in graph.nodes_view


def test_graph_removes_node_after_removing_its_edges():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_node(Node(id="C"))

    graph.add_edge(Edge(source="A", target="B", id="e1"))
    graph.add_edge(Edge(source="B", target="C", id="e2"))

    graph.remove_edge("e1")
    graph.remove_edge("e2")
    graph.remove_node("B")

    assert "B" not in graph.nodes_view
    assert len(graph.nodes_view) == 2
    assert len(graph.edges_view) == 0


def test_graph_removes_only_selected_edge():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    graph.add_edge(Edge(source="A", target="B", id="e1"))
    graph.add_edge(Edge(source="A", target="B", id="e2"))

    graph.remove_edge("e1")

    assert "e1" not in graph.edges_view
    assert "e2" in graph.edges_view


def test_graph_can_remove_all_nodes_and_edges():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_edge(Edge(source="A", target="B", id="e1"))

    graph.remove_edge("e1")
    graph.remove_node("A")
    graph.remove_node("B")

    assert len(graph.nodes_view) == 0
    assert len(graph.edges_view) == 0


def test_graph_gets_existing_node():
    graph = Graph()
    node = Node(id="A")

    graph.add_node(node)

    assert graph.get_node("A") is node


def test_graph_gets_existing_edge():
    graph = Graph()
    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    edge = Edge(source="A", target="B", id="e1")
    graph.add_edge(edge)

    assert graph.get_edge("e1") is edge


def test_graph_rejects_getting_nonexistent_node():
    graph = Graph()

    with pytest.raises(ValueError, match="does not exist"):
        graph.get_node("unknown")


def test_graph_rejects_getting_nonexistent_edge():
    graph = Graph()

    with pytest.raises(ValueError, match="does not exist"):
        graph.get_edge("unknown")


def test_graph_gets_correct_node_among_multiple():
    graph = Graph()

    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_node(Node(id="C"))

    assert graph.get_node("B").id == "B"


def test_graph_gets_correct_edge_among_multiple():
    graph = Graph()

    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_node(Node(id="C"))

    graph.add_edge(Edge(source="A", target="B", id="e1"))
    graph.add_edge(Edge(source="B", target="C", id="e2"))

    assert graph.get_edge("e2").source == "B"
    assert graph.get_edge("e2").target == "C"


def test_graph_gets_node_with_attributes():
    graph = Graph()

    node = Node(
        id="A",
        attributes={"name": "Marko", "age": 25}
    )

    graph.add_node(node)

    found_node = graph.get_node("A")

    assert found_node.attributes_view["name"] == "Marko"
    assert found_node.attributes_view["age"] == 25


def test_graph_gets_edge_with_attributes():
    graph = Graph()

    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))

    edge = Edge(
        source="A",
        target="B",
        id="e1",
        attributes={"weight": 10}
    )

    graph.add_edge(edge)

    assert graph.get_edge("e1").attributes_view["weight"] == 10


def test_graph_allows_disconnected_nodes():
    graph = Graph()

    graph.add_node(Node(id="A"))
    graph.add_node(Node(id="B"))
    graph.add_node(Node(id="C"))

    assert len(graph.nodes_view) == 3
    assert len(graph.edges_view) == 0


def test_graph_allows_disconnected_components():
    graph = Graph()

    for node_id in ["A", "B", "C", "D"]:
        graph.add_node(Node(id=node_id))

    graph.add_edge(Edge(id="e1", source="A", target="B"))
    graph.add_edge(Edge(id="e2", source="C", target="D"))

    assert len(graph.nodes_view) == 4
    assert len(graph.edges_view) == 2


def test_graph_allows_directed_cycle():
    graph = Graph(directed=True)

    for node_id in ["A", "B", "C"]:
        graph.add_node(Node(id=node_id))

    graph.add_edge(Edge(id="e1", source="A", target="B"))
    graph.add_edge(Edge(id="e2", source="B", target="C"))
    graph.add_edge(Edge(id="e3", source="C", target="A"))

    assert len(graph.edges_view) == 3


def test_graph_allows_undirected_cycle():
    graph = Graph(directed=False)

    for node_id in ["A", "B", "C"]:
        graph.add_node(Node(id=node_id))

    graph.add_edge(Edge(id="e1", source="A", target="B"))
    graph.add_edge(Edge(id="e2", source="B", target="C"))
    graph.add_edge(Edge(id="e3", source="C", target="A"))

    assert graph.directed is False
    assert len(graph.edges_view) == 3


def test_graph_allows_isolated_node_with_connected_nodes():
    graph = Graph()

    for node_id in ["A", "B", "C"]:
        graph.add_node(Node(id=node_id))

    graph.add_edge(Edge(id="e1", source="A", target="B"))

    assert "C" in graph.nodes_view
    assert len(graph.edges_view) == 1


def test_graph_allows_empty_graph():
    graph = Graph()

    assert len(graph.nodes_view) == 0
    assert len(graph.edges_view) == 0



def test_graph_supports_200_nodes():
    graph = Graph()

    for i in range(200):
        graph.add_node(Node(id=f"node_{i}"))

    assert len(graph.nodes_view) == 200
    assert graph.get_node("node_0").id == "node_0"
    assert graph.get_node("node_199").id == "node_199"


def test_graph_supports_200_nodes_and_199_edges():
    graph = Graph()

    for i in range(200):
        graph.add_node(Node(id=f"node_{i}"))

    for i in range(199):
        graph.add_edge(
            Edge(
                id=f"edge_{i}",
                source=f"node_{i}",
                target=f"node_{i + 1}"
            )
        )

    assert len(graph.nodes_view) == 200
    assert len(graph.edges_view) == 199


def test_graph_supports_large_cyclic_graph():
    graph = Graph(directed=True)

    for i in range(250):
        graph.add_node(Node(id=f"node_{i}"))

    for i in range(250):
        graph.add_edge(
            Edge(
                id=f"edge_{i}",
                source=f"node_{i}",
                target=f"node_{(i + 1) % 250}"
            )
        )

    assert len(graph.nodes_view) == 250
    assert len(graph.edges_view) == 250

    assert graph.get_edge("edge_249").target == "node_0"

