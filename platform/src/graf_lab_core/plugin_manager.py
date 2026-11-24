"""Discover installed plugins registered through Python entry points."""

from importlib.metadata import entry_points

from graf_lab_api.plugins import DataSourcePlugin, VisualizerPlugin


def discover_data_sources() -> dict[str, DataSourcePlugin]:
    """Return data source instances indexed by their registered names."""
    return _discover_plugins("graf_lab.data_sources", DataSourcePlugin)


def discover_visualizers() -> dict[str, VisualizerPlugin]:
    """Return visualizer instances indexed by their registered names."""
    return _discover_plugins("graf_lab.visualizers", VisualizerPlugin)


def _discover_plugins[PluginType](
    group: str,
    interface: type[PluginType],
) -> dict[str, PluginType]:
    """Load plugin classes and create a fresh instance of each without arguments.

    Raise ValueError for duplicate names, TypeError for an invalid interface,
    or RuntimeError if loading or constructing a plugin fails. A failed
    discovery does not return a partial collection.
    """
    plugins: dict[str, PluginType] = {}

    for registration in entry_points(group=group):
        if registration.name in plugins:
            raise ValueError(
                f"Duplicate plugin name '{registration.name}' in group '{group}'"
            )

        try:
            plugin_class = registration.load()
        except Exception as error:
            raise RuntimeError(
                f"Could not load plugin '{registration.name}' in group '{group}'"
            ) from error

        if not isinstance(plugin_class, type) or not issubclass(
            plugin_class, interface
        ):
            raise TypeError(
                f"Plugin '{registration.name}' in group '{group}' must inherit "
                f"{interface.__name__}"
            )

        try:
            plugins[registration.name] = plugin_class()
        except Exception as error:
            raise RuntimeError(
                f"Could not create plugin '{registration.name}' in group '{group}'"
            ) from error

    return plugins
