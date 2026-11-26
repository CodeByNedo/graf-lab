import pytest

from graf_lab_api.models import Graph, Node, Edge
from graf_lab_api.plugins import DataSourcePlugin
from graf_lab_core.workspace import Workspace
from graf_lab_core.workspace_manager import WorkspaceManager


class StubDataSource(DataSourcePlugin):

    def __init__(self):
        self.load_count = 0

    def load(self, parameters):
        self.load_count += 1

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


class AlternativeDataSource(DataSourcePlugin):

    def load(self, parameters):
        graph = Graph(directed=False)

        graph.add_node(Node(
            id="a",
            attributes={"name": "Belgrade"}
        ))

        graph.add_node(Node(
            id="b",
            attributes={"name": "Novi Sad"}
        ))

        graph.add_edge(Edge(id="ab", source="a", target="b"))

        return graph


class FailingDataSource(DataSourcePlugin):

    def load(self, parameters):
        raise ValueError("Unable to load graph")


@pytest.fixture
def manager():
    return WorkspaceManager()


@pytest.fixture
def source():
    return StubDataSource()


def test_manager_initially_has_no_workspaces(manager):
    assert len(manager.workspaces_view) == 0


def test_manager_initially_has_no_active_workspace(manager):
    assert manager.active_workspace is None


def test_manager_creates_workspace(manager, source):
    workspace = manager.create_workspace(source, {})

    assert isinstance(workspace, Workspace)
    assert workspace.id in manager.workspaces_view
    assert len(manager.workspaces_view) == 1


def test_created_workspace_becomes_active(manager, source):
    workspace = manager.create_workspace(source, {})

    assert manager.active_workspace is workspace


def test_manager_creates_multiple_workspaces(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})

    assert len(manager.workspaces_view) == 2
    assert first.id != second.id
    assert manager.active_workspace is second


def test_manager_creates_workspaces_with_same_source(manager, source):
    first = manager.create_workspace(source, {"path": "test.json"})
    second = manager.create_workspace(source, {"path": "test.json"})

    assert first.source is second.source
    assert first.id != second.id
    assert first.current_graph is not second.current_graph


def test_manager_creates_workspaces_with_different_sources(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(AlternativeDataSource(), {})

    assert first.source is not second.source
    assert set(first.current_graph.nodes_view) == {"1", "2", "3"}
    assert set(second.current_graph.nodes_view) == {"a", "b"}


def test_manager_preserves_different_source_parameters(manager, source):
    first = manager.create_workspace(source, {"path": "first.json"})
    second = manager.create_workspace(source, {"path": "second.json"})

    assert first.parameters["path"] == "first.json"
    assert second.parameters["path"] == "second.json"


def test_manager_gets_workspace_by_id(manager, source):
    workspace = manager.create_workspace(source, {})

    assert manager.get_workspace(workspace.id) is workspace


def test_manager_gets_nonexistent_workspace(manager):
    with pytest.raises(ValueError, match="does not exist"):
        manager.get_workspace("nonexistent")


def test_manager_selects_workspace(manager, source):
    first = manager.create_workspace(source, {})
    manager.create_workspace(source, {})

    manager.select_workspace(first.id)

    assert manager.active_workspace is first


def test_manager_selects_already_active_workspace(manager, source):
    workspace = manager.create_workspace(source, {})

    manager.select_workspace(workspace.id)

    assert manager.active_workspace is workspace


def test_manager_invalid_selection_preserves_active_workspace(
    manager, source
):
    workspace = manager.create_workspace(source, {})

    with pytest.raises(ValueError, match="does not exist"):
        manager.select_workspace("nonexistent")

    assert manager.active_workspace is workspace


def test_manager_deletes_workspace(manager, source):
    workspace = manager.create_workspace(source, {})

    manager.delete_workspace(workspace.id)

    assert workspace.id not in manager.workspaces_view


def test_manager_deletes_inactive_workspace(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})

    manager.delete_workspace(first.id)

    assert manager.active_workspace is second
    assert len(manager.workspaces_view) == 1


def test_manager_deletes_active_workspace(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})

    manager.delete_workspace(second.id)

    assert manager.active_workspace is first


def test_manager_selects_first_remaining_workspace_after_deletion(
    manager, source
):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})
    third = manager.create_workspace(source, {})

    manager.delete_workspace(third.id)

    assert manager.active_workspace is first
    assert second.id in manager.workspaces_view


def test_manager_deletes_last_workspace(manager, source):
    workspace = manager.create_workspace(source, {})

    manager.delete_workspace(workspace.id)

    assert manager.active_workspace is None
    assert len(manager.workspaces_view) == 0


def test_manager_deletes_nonexistent_workspace(manager, source):
    workspace = manager.create_workspace(source, {})

    with pytest.raises(ValueError, match="does not exist"):
        manager.delete_workspace("nonexistent")

    assert manager.active_workspace is workspace
    assert len(manager.workspaces_view) == 1


def test_deleted_workspace_cannot_be_selected(manager, source):
    workspace = manager.create_workspace(source, {})

    manager.delete_workspace(workspace.id)

    with pytest.raises(ValueError, match="does not exist"):
        manager.select_workspace(workspace.id)


def test_manager_creates_workspace_after_deleting_all(manager, source):
    first = manager.create_workspace(source, {})
    manager.delete_workspace(first.id)

    second = manager.create_workspace(source, {})

    assert manager.active_workspace is second
    assert first.id != second.id


def test_manager_workspaces_view_is_read_only(manager, source):
    workspace = manager.create_workspace(source, {})

    with pytest.raises(TypeError):
        manager.workspaces_view["another"] = workspace


def test_manager_instances_are_independent(source):
    first_manager = WorkspaceManager()
    second_manager = WorkspaceManager()

    first_manager.create_workspace(source, {})

    assert len(first_manager.workspaces_view) == 1
    assert len(second_manager.workspaces_view) == 0
    assert second_manager.active_workspace is None


def test_manager_preserves_graph_state_when_switching(manager, source):
    first = manager.create_workspace(source, {})
    manager.active_workspace.search("student")

    second = manager.create_workspace(source, {})
    manager.active_workspace.search("Ana")

    manager.select_workspace(first.id)

    assert set(manager.active_workspace.current_graph.nodes_view) == {
        "1", "2"
    }

    manager.select_workspace(second.id)

    assert set(manager.active_workspace.current_graph.nodes_view) == {
        "3"
    }


def test_manager_preserves_query_history_when_switching(manager, source):
    first = manager.create_workspace(source, {})
    manager.active_workspace.search("student")
    manager.active_workspace.filter("age > 20")

    second = manager.create_workspace(source, {})
    manager.active_workspace.search("Ana")

    manager.select_workspace(first.id)

    assert manager.active_workspace.query_history == (
        ("search", "student"),
        ("filter", "age > 20"),
    )

    manager.select_workspace(second.id)

    assert manager.active_workspace.query_history == (
        ("search", "Ana"),
    )


def test_manager_applies_queries_only_to_active_workspace(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})

    manager.active_workspace.search("student")
    manager.active_workspace.filter("age > 20")

    assert set(second.current_graph.nodes_view) == {"1"}
    assert set(first.current_graph.nodes_view) == {"1", "2", "3"}
    assert first.query_history == ()


def test_manager_reset_affects_only_active_workspace(manager, source):
    first = manager.create_workspace(source, {})
    manager.active_workspace.search("student")

    second = manager.create_workspace(source, {})
    manager.active_workspace.search("Ana")
    manager.active_workspace.reset()

    assert set(first.current_graph.nodes_view) == {"1", "2"}
    assert first.query_history == (("search", "student"),)

    assert set(second.current_graph.nodes_view) == {"1", "2", "3"}
    assert second.query_history == ()


def test_manager_switching_does_not_reload_graphs(manager, source):
    first = manager.create_workspace(source, {})
    second = manager.create_workspace(source, {})

    manager.select_workspace(first.id)
    manager.select_workspace(second.id)
    manager.select_workspace(first.id)

    assert source.load_count == 2


def test_manager_preserves_graph_modifications_when_switching(
    manager, source
):
    first = manager.create_workspace(source, {})

    first.current_graph.get_node("1").set_attribute("age", 50)

    second = manager.create_workspace(source, {})

    manager.select_workspace(first.id)

    assert (
        manager.active_workspace.current_graph
        .get_node("1").attributes_view["age"] == 50
    )

    assert second.current_graph.get_node("1").attributes_view["age"] == 25


def test_manager_failed_creation_preserves_existing_state(manager, source):
    workspace = manager.create_workspace(source, {})

    with pytest.raises(ValueError, match="Unable to load graph"):
        manager.create_workspace(FailingDataSource(), {})

    assert manager.active_workspace is workspace
    assert len(manager.workspaces_view) == 1


def test_manager_failed_creation_leaves_empty_manager(manager):
    with pytest.raises(ValueError, match="Unable to load graph"):
        manager.create_workspace(FailingDataSource(), {})

    assert manager.active_workspace is None
    assert len(manager.workspaces_view) == 0