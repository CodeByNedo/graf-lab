
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4


AttributeValue = int | str | float | date

_MISSING = object()


@dataclass(init=False)
class Node:
    """Represents a graph node with a unique ID and typed attributes."""

    _id: str = field(repr=False)
    _attributes: dict[str, AttributeValue] = field(
        default_factory=dict,
        repr=False
    )

    def __init__(
        self,
        id: str | object = _MISSING,
        attributes: dict[str, AttributeValue] | object = _MISSING
    ):
        """Initialize a node with an optional ID and attributes."""

        if id is _MISSING:
            id = str(uuid4())

        if not isinstance(id, str) or not id.strip():
            raise ValueError("Node ID must be a non-empty string")

        if attributes is _MISSING:
            attributes = {}

        if not isinstance(attributes, dict):
            raise ValueError("Node attributes must be a dictionary")

        self._id = id
        self._attributes = {}

        for name, value in attributes.items():
            self.set_attribute(name, value)

    @property
    def id(self) -> str:
        """Return the node ID."""
        return self._id

    @property
    def attributes_view(self) -> Mapping[str, AttributeValue]:
        """Return a read-only view of the node attributes."""
        return MappingProxyType(self._attributes)

    def set_attribute(self, name: str, value: AttributeValue) -> None:
        """Set an attribute, allowing int, str, float, or date values."""

        if not isinstance(name, str):
            raise ValueError("Attribute name must be a string")

        if type(value) not in (int, str, float, date):
            raise ValueError(
                f"Unsupported attribute type for '{name}'"
            )

        self._attributes[name] = value
