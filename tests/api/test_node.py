
from datetime import date
from uuid import UUID

import pytest

from graf_lab_api.models.node import Node


# --------------------------------------------------
# Testovi identifikatora čvora
# --------------------------------------------------

def test_node_with_custom_id():
    node = Node(id="student_1")

    assert node.id == "student_1"


def test_node_generates_uuid():
    node = Node()

    generated_uuid = UUID(node.id)

    assert generated_uuid.version == 4


def test_nodes_generate_different_ids():
    node1 = Node()
    node2 = Node()

    assert node1.id != node2.id


@pytest.mark.parametrize(
    "invalid_id",
    ["", "   ", None, 123]
)
def test_node_rejects_invalid_id(invalid_id):
    with pytest.raises(ValueError):
        Node(id=invalid_id)


# --------------------------------------------------
# Testovi početnih atributa
# --------------------------------------------------

def test_node_with_attributes():
    node = Node(
        id="student_1",
        attributes={
            "name": "Marko",
            "age": 23
        }
    )

    assert node.attributes_view["name"] == "Marko"
    assert node.attributes_view["age"] == 23


def test_node_without_attributes():
    node = Node()

    assert dict(node.attributes_view) == {}


def test_node_with_empty_attributes():
    node = Node(attributes={})

    assert dict(node.attributes_view) == {}


@pytest.mark.parametrize(
    "value",
    [
        23,
        "Marko",
        9.5,
        date(2026, 11, 8)
    ]
)
def test_node_accepts_valid_attribute_types(value):
    node = Node(attributes={"test": value})

    assert node.attributes_view["test"] == value


@pytest.mark.parametrize(
    "value",
    [
        [1, 2, 3],
        {"nested": "value"},
        None,
        True
    ]
)
def test_node_rejects_invalid_attribute_types(value):
    with pytest.raises(ValueError):
        Node(attributes={"test": value})


def test_node_rejects_invalid_attribute_name():
    with pytest.raises(ValueError):
        Node(attributes={123: "Marko"})


@pytest.mark.parametrize(
    "invalid_attributes",
    [
        None,
        ["Marko", 23],
        "invalid"
    ]
)
def test_node_rejects_non_dictionary_attributes(invalid_attributes):
    with pytest.raises(ValueError):
        Node(attributes=invalid_attributes)


# --------------------------------------------------
# Testovi izmjene atributa
# --------------------------------------------------

def test_node_set_valid_attribute():
    node = Node()

    node.set_attribute("age", 23)
    node.set_attribute("age", 24)

    assert node.attributes_view["age"] == 24


@pytest.mark.parametrize(
    "value",
    [
        [1, 2, 3],
        {"nested": "value"},
        None,
        True
    ]
)
def test_node_set_invalid_attribute_value(value):
    node = Node()

    with pytest.raises(ValueError):
        node.set_attribute("test", value)


def test_node_set_invalid_attribute_name():
    node = Node()

    with pytest.raises(ValueError):
        node.set_attribute(123, "Marko")


# --------------------------------------------------
# Testovi enkapsulacije atributa
# --------------------------------------------------

def test_nodes_have_independent_attributes():
    node1 = Node()
    node2 = Node()

    node1.set_attribute("name", "Marko")

    assert dict(node1.attributes_view) == {"name": "Marko"}
    assert dict(node2.attributes_view) == {}


def test_node_attributes_cannot_be_modified_directly():
    node = Node(attributes={"age": 23})

    with pytest.raises(TypeError):
        node.attributes_view["age"] = 24

    assert node.attributes_view["age"] == 23


def test_node_attributes_view_reflects_changes():
    node = Node(attributes={"age": 23})

    view = node.attributes_view

    node.set_attribute("age", 24)

    assert view["age"] == 24


def test_node_id_cannot_be_changed():
    node = Node(id="student_1")

    with pytest.raises(AttributeError):
        node.id = "student_2"

    assert node.id == "student_1"


def test_generated_node_id_cannot_be_changed():
    node = Node()

    original_id = node.id

    with pytest.raises(AttributeError):
        node.id = "another_id"

    assert node.id == original_id