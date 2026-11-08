
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4


AttributeValue = int | str | float | date

_MISSING = object()


@dataclass(init=False)
class Edge:
    """Represents a graph edge connecting two nodes by their IDs."""

    _id: str = field(repr=False)
    _source: str
    _target: str
    _attributes: dict[str, AttributeValue] = field(
        default_factory=dict,
        repr=False
    )

    def __init__(
        self,
        source: str,
        target: str,
        id: str | object = _MISSING,
        attributes: dict[str, AttributeValue] | object = _MISSING
    ):
        """Initialize an edge with endpoints, an optional ID, and attributes."""

        if id is _MISSING:
            id = str(uuid4())

        if not isinstance(id, str) or not id.strip():
            raise ValueError("Edge ID must be a non-empty string")

        if not isinstance(source, str) or not source.strip():
            raise ValueError("Edge source must be a non-empty string")

        if not isinstance(target, str) or not target.strip():
            raise ValueError("Edge target must be a non-empty string")

        if attributes is _MISSING:
            attributes = {}

        if not isinstance(attributes, dict):
            raise ValueError("Edge attributes must be a dictionary")

        self._id = id
        self._source = source
        self._target = target
        self._attributes = {}

        for name, value in attributes.items():
            self.set_attribute(name, value)

    @property
    def id(self) -> str:
        """Return the edge ID."""
        return self._id

    @property
    def source(self) -> str:
        """Return the source node ID."""
        return self._source

    @property
    def target(self) -> str:
        """Return the target node ID."""
        return self._target

    @property
    def attributes_view(self) -> Mapping[str, AttributeValue]:
        """Return a read-only view of the edge attributes."""
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
