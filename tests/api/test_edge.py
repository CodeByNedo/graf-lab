
from uuid import UUID

import pytest

from graf_lab_api.models.edge import Edge


def test_edge_with_custom_id():
    edge = Edge(source="A", target="B", id="edge_1")

    assert edge.id == "edge_1"
    assert edge.source == "A"
    assert edge.target == "B"


def test_edge_generates_uuid():
    edge = Edge(source="A", target="B")

    assert UUID(edge.id).version == 4


def test_edges_generate_different_ids():
    edge1 = Edge(source="A", target="B")
    edge2 = Edge(source="A", target="B")

    assert edge1.id != edge2.id


@pytest.mark.parametrize("invalid_id", ["", "   ", 123, True])
def test_edge_rejects_invalid_id(invalid_id):
    with pytest.raises(ValueError):
        Edge(source="A", target="B", id=invalid_id)


@pytest.mark.parametrize("invalid_source", ["", "   ", None, 123])
def test_edge_rejects_invalid_source(invalid_source):
    with pytest.raises(ValueError):
        Edge(source=invalid_source, target="B")


@pytest.mark.parametrize("invalid_target", ["", "   ", None, 123])
def test_edge_rejects_invalid_target(invalid_target):
    with pytest.raises(ValueError):
        Edge(source="A", target=invalid_target)


def test_edge_allows_self_loop():
    edge = Edge(source="A", target="A")

    assert edge.source == edge.target


def test_edge_id_cannot_be_changed():
    edge = Edge(source="A", target="B")

    with pytest.raises(AttributeError):
        edge.id = "new_id"


def test_edge_source_cannot_be_changed():
    edge = Edge(source="A", target="B")

    with pytest.raises(AttributeError):
        edge.source = "C"


def test_edge_target_cannot_be_changed():
    edge = Edge(source="A", target="B")

    with pytest.raises(AttributeError):
        edge.target = "C"



from datetime import date


def test_edge_with_attributes():
    edge = Edge(
        source="A",
        target="B",
        attributes={"weight": 5, "label": "poznaje"}
    )

    assert edge.attributes_view["weight"] == 5
    assert edge.attributes_view["label"] == "poznaje"


def test_edge_without_attributes():
    edge = Edge(source="A", target="B")

    assert dict(edge.attributes_view) == {}


def test_edge_with_empty_attributes():
    edge = Edge(source="A", target="B", attributes={})

    assert dict(edge.attributes_view) == {}


@pytest.mark.parametrize(
    "value",
    [23, "poznaje", 9.5, date(2026, 11, 8)]
)
def test_edge_accepts_valid_attribute_types(value):
    edge = Edge(
        source="A",
        target="B",
        attributes={"test": value}
    )

    assert edge.attributes_view["test"] == value


@pytest.mark.parametrize(
    "value",
    [[1, 2, 3], {"nested": "value"}, None, True]
)
def test_edge_rejects_invalid_attribute_types(value):
    with pytest.raises(ValueError):
        Edge(
            source="A",
            target="B",
            attributes={"test": value}
        )


@pytest.mark.parametrize("attributes", [None, [], "invalid"])
def test_edge_rejects_non_dictionary_attributes(attributes):
    with pytest.raises(ValueError):
        Edge(
            source="A",
            target="B",
            attributes=attributes
        )


def test_edge_rejects_invalid_attribute_name():
    with pytest.raises(ValueError):
        Edge(
            source="A",
            target="B",
            attributes={123: "value"}
        )


def test_edge_set_valid_attribute():
    edge = Edge(source="A", target="B")

    edge.set_attribute("weight", 5)
    edge.set_attribute("weight", 10)

    assert edge.attributes_view["weight"] == 10


@pytest.mark.parametrize(
    "value",
    [[1, 2, 3], {"nested": "value"}, None, True]
)
def test_edge_set_invalid_attribute_value(value):
    edge = Edge(source="A", target="B")

    with pytest.raises(ValueError):
        edge.set_attribute("test", value)


def test_edge_set_invalid_attribute_name():
    edge = Edge(source="A", target="B")

    with pytest.raises(ValueError):
        edge.set_attribute(123, "value")


def test_edges_have_independent_attributes():
    edge1 = Edge(source="A", target="B")
    edge2 = Edge(source="A", target="B")

    edge1.set_attribute("weight", 5)

    assert "weight" not in edge2.attributes_view


def test_edge_attributes_cannot_be_modified_directly():
    edge = Edge(
        source="A",
        target="B",
        attributes={"weight": 5}
    )

    with pytest.raises(TypeError):
        edge.attributes_view["weight"] = 10

    assert edge.attributes_view["weight"] == 5


def test_edge_attributes_view_reflects_changes():
    edge = Edge(
        source="A",
        target="B",
        attributes={"weight": 5}
    )

    view = edge.attributes_view

    edge.set_attribute("weight", 10)

    assert view["weight"] == 10


def test_edge_rejects_explicit_none_id():
    with pytest.raises(ValueError):
        Edge(source="A", target="B", id=None)
