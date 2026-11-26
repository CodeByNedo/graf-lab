import pytest

from graf_lab_api.models import Graph, Node, Edge
from graf_lab_api.plugins import DataSourcePlugin
from graf_lab_core.workspace import Workspace


class StubDataSource(DataSourcePlugin):

    def load(self, parameters):
        graph = Graph(directed=True)

        graph.add_node(Node(
            id="1",
            attributes={"name": "Marko", "age": 25, "role": "student"}
        ))

        graph.add_node(Node(
            id="2",
            attributes={"name": "Petar", "age": 19, "role": "student"}
        ))

        graph.add_node(Node(
            id="3",
            attributes={"name": "Ana", "age": 35, "role": "professor"}
        ))

        graph.add_edge(Edge(id="e1", source="1", target="2"))
        graph.add_edge(Edge(id="e2", source="2", target="3"))

        return graph


@pytest.fixture
def workspace():
    return Workspace(
        source=StubDataSource(),
        parameters={"path": "test.json"}
    )


def test_workspace_has_id(workspace):
    assert isinstance(workspace.id, str)
    assert workspace.id


def test_workspace_has_source(workspace):
    assert isinstance(workspace.source, StubDataSource)


def test_workspace_stores_parameters(workspace):
    assert workspace.parameters == {"path": "test.json"}


def test_workspace_loads_original_graph(workspace):
    assert len(workspace.original_graph.nodes_view) == 3
    assert len(workspace.original_graph.edges_view) == 2


def test_workspace_initial_current_graph(workspace):
    assert len(workspace.current_graph.nodes_view) == 3
    assert len(workspace.current_graph.edges_view) == 2


def test_workspace_initial_history_is_empty(workspace):
    assert workspace.query_history == ()

def test_workspaces_have_unique_ids():
    source = StubDataSource()

    first = Workspace(source, {"path": "test.json"})
    second = Workspace(source, {"path": "test.json"})

    assert first.id != second.id

def test_workspace_copies_parameters():
    parameters = {"path": "test.json"}
    workspace = Workspace(StubDataSource(), parameters)

    parameters["path"] = "other.json"

    assert workspace.parameters["path"] == "test.json"

def test_workspace_parameters_are_read_only(workspace):
    with pytest.raises(TypeError):
        workspace.parameters["path"] = "other.json"

def test_current_graph_changes_do_not_affect_original(workspace):
    workspace.current_graph.remove_edge("e1")
    workspace.current_graph.remove_node("1")

    assert "1" in workspace.original_graph.nodes_view
    assert "e1" in workspace.original_graph.edges_view

def test_current_node_changes_do_not_affect_original(workspace):
    workspace.current_graph.get_node("1").set_attribute("age", 50)

    assert workspace.original_graph.get_node("1").attributes_view["age"] == 25

def test_current_edge_changes_do_not_affect_original(workspace):
    workspace.current_graph.get_edge("e1").set_attribute("weight", 10)

    assert "weight" not in (
        workspace.original_graph.get_edge("e1").attributes_view
    )

def test_original_graph_property_returns_independent_copy(workspace):
    original = workspace.original_graph
    original.get_node("1").set_attribute("age", 100)

    assert workspace.original_graph.get_node("1").attributes_view["age"] == 25

def test_workspaces_have_independent_graphs():
    source = StubDataSource()

    first = Workspace(source, {"path": "test.json"})
    second = Workspace(source, {"path": "test.json"})

    first.current_graph.get_node("1").set_attribute("age", 100)

    assert second.current_graph.get_node("1").attributes_view["age"] == 25

def test_workspace_search(workspace):
    workspace.search("student")

    assert set(workspace.current_graph.nodes_view) == {"1", "2"}
    assert set(workspace.current_graph.edges_view) == {"e1"}


def test_workspace_filter(workspace):
    workspace.filter("age > 20")

    assert set(workspace.current_graph.nodes_view) == {"1", "3"}
    assert len(workspace.current_graph.edges_view) == 0


def test_workspace_successive_searches(workspace):
    workspace.search("student")
    workspace.search("Marko")

    assert set(workspace.current_graph.nodes_view) == {"1"}


def test_workspace_successive_filters(workspace):
    workspace.filter("age > 18")
    workspace.filter("age < 30")

    assert set(workspace.current_graph.nodes_view) == {"1", "2"}


def test_workspace_search_then_filter(workspace):
    workspace.search("student")
    workspace.filter("age > 20")

    assert set(workspace.current_graph.nodes_view) == {"1"}


def test_workspace_filter_then_search(workspace):
    workspace.filter("age > 20")
    workspace.search("student")

    assert set(workspace.current_graph.nodes_view) == {"1"}


def test_workspace_query_history_order(workspace):
    workspace.search("student")
    workspace.filter("age > 18")
    workspace.search("Marko")

    assert workspace.query_history == (
        ("search", "student"),
        ("filter", "age > 18"),
        ("search", "Marko"),
    )


def test_workspace_query_history_is_immutable(workspace):
    workspace.search("student")

    history = workspace.query_history

    with pytest.raises(TypeError):
        history[0] = ("search", "Ana")

    assert workspace.query_history == (("search", "student"),)


def test_workspace_search_without_matches(workspace):
    workspace.search("nonexistent")

    assert len(workspace.current_graph.nodes_view) == 0
    assert len(workspace.current_graph.edges_view) == 0


def test_workspace_filter_without_matches(workspace):
    workspace.filter("age > 100")

    assert len(workspace.current_graph.nodes_view) == 0
    assert len(workspace.current_graph.edges_view) == 0


def test_workspace_empty_search_preserves_current_graph(workspace):
    workspace.search("student")
    workspace.search("")

    assert set(workspace.current_graph.nodes_view) == {"1", "2"}


def test_workspace_empty_filter_preserves_current_graph(workspace):
    workspace.search("student")
    workspace.filter("")

    assert set(workspace.current_graph.nodes_view) == {"1", "2"}


@pytest.mark.parametrize("query", [
    "invalid query",
    "age > abc",
    "age === 20",
])
def test_workspace_invalid_filter_preserves_state(workspace, query):
    workspace.search("student")

    previous_graph = workspace.current_graph
    previous_history = workspace.query_history

    with pytest.raises(ValueError):
        workspace.filter(query)

    assert workspace.current_graph is previous_graph
    assert workspace.query_history == previous_history


def test_workspace_queries_preserve_original_graph(workspace):
    workspace.search("student")
    workspace.filter("age > 20")

    assert set(workspace.original_graph.nodes_view) == {"1", "2", "3"}
    assert set(workspace.original_graph.edges_view) == {"e1", "e2"}


def test_workspace_reset_restores_graph(workspace):
    workspace.search("student")
    workspace.filter("age > 20")
    workspace.reset()

    assert set(workspace.current_graph.nodes_view) == {"1", "2", "3"}
    assert set(workspace.current_graph.edges_view) == {"e1", "e2"}


def test_workspace_reset_clears_history(workspace):
    workspace.search("student")
    workspace.filter("age > 20")
    workspace.reset()

    assert workspace.query_history == ()


def test_workspace_reset_restores_attributes(workspace):
    workspace.current_graph.get_node("1").set_attribute("age", 100)
    workspace.current_graph.get_edge("e1").set_attribute("weight", 10)

    workspace.reset()

    assert workspace.current_graph.get_node("1").attributes_view["age"] == 25
    assert "weight" not in (
        workspace.current_graph.get_edge("e1").attributes_view
    )


def test_workspace_reset_preserves_graph_independence(workspace):
    workspace.reset()
    workspace.current_graph.get_node("1").set_attribute("age", 100)

    assert workspace.original_graph.get_node("1").attributes_view["age"] == 25


def test_workspace_multiple_resets(workspace):
    workspace.search("student")
    workspace.reset()
    workspace.reset()

    assert len(workspace.current_graph.nodes_view) == 3
    assert len(workspace.current_graph.edges_view) == 2
    assert workspace.query_history == ()


def test_workspace_search_after_reset(workspace):
    workspace.search("student")
    workspace.reset()
    workspace.search("Ana")

    assert set(workspace.current_graph.nodes_view) == {"3"}
    assert workspace.query_history == (("search", "Ana"),)


def test_workspaces_have_independent_query_histories():
    source = StubDataSource()

    first = Workspace(source, {"path": "test.json"})
    second = Workspace(source, {"path": "test.json"})

    first.search("student")
    second.filter("age > 20")

    assert first.query_history == (("search", "student"),)
    assert second.query_history == (("filter", "age > 20"),)

    assert set(first.current_graph.nodes_view) == {"1", "2"}
    assert set(second.current_graph.nodes_view) == {"1", "3"}


def test_workspace_reset_does_not_affect_other_workspace():
    source = StubDataSource()

    first = Workspace(source, {"path": "test.json"})
    second = Workspace(source, {"path": "test.json"})

    first.search("student")
    second.search("Ana")

    first.reset()

    assert len(first.current_graph.nodes_view) == 3
    assert set(second.current_graph.nodes_view) == {"3"}
    assert second.query_history == (("search", "Ana"),)


class SharedGraphDataSource(DataSourcePlugin):

    def __init__(self):
        self.graph = StubDataSource().load({})
        self.load_count = 0

    def load(self, parameters):
        self.load_count += 1
        return self.graph


def test_workspaces_are_independent_with_shared_source_graph():
    source = SharedGraphDataSource()

    first = Workspace(source, {})
    second = Workspace(source, {})

    first.current_graph.get_node("1").set_attribute("age", 100)
    first.current_graph.get_edge("e1").set_attribute("weight", 10)

    assert second.current_graph.get_node("1").attributes_view["age"] == 25
    assert source.graph.get_node("1").attributes_view["age"] == 25

    assert "weight" not in (
        second.current_graph.get_edge("e1").attributes_view
    )
    assert "weight" not in source.graph.get_edge("e1").attributes_view


def test_workspace_loads_source_only_once():
    source = SharedGraphDataSource()
    workspace = Workspace(source, {})

    workspace.search("student")
    workspace.filter("age > 20")
    workspace.reset()

    assert source.load_count == 1


def test_workspace_preserves_undirected_graph():
    source = SharedGraphDataSource()
    source.graph = Graph(directed=False)

    source.graph.add_node(Node(
        id="1",
        attributes={"name": "Marko"}
    ))
    source.graph.add_node(Node(
        id="2",
        attributes={"name": "Petar"}
    ))
    source.graph.add_edge(Edge(
        id="e1",
        source="1",
        target="2"
    ))

    workspace = Workspace(source, {})

    assert workspace.original_graph.directed is False
    assert workspace.current_graph.directed is False

    workspace.search("Marko")
    assert workspace.current_graph.directed is False

    workspace.reset()
    assert workspace.current_graph.directed is False
    assert len(workspace.current_graph.edges_view) == 1
