from collections.abc import Mapping
from types import MappingProxyType

from graf_lab_api.plugins import DataSourcePlugin

from .workspace import Workspace


class WorkspaceManager:
    """Manage multiple independent graph workspaces."""

    def __init__(self):
        self._workspaces: dict[str, Workspace] = {}
        self._active_workspace_id: str | None = None

    @property
    def workspaces_view(self) -> Mapping[str, Workspace]:
        """Return a read-only view of registered workspaces."""
        return MappingProxyType(self._workspaces)

    @property
    def active_workspace(self) -> Workspace | None:
        """Return the active workspace, if one exists."""
        if self._active_workspace_id is None:
            return None

        return self._workspaces[self._active_workspace_id]

    def create_workspace(
        self,
        source: DataSourcePlugin,
        parameters: Mapping[str, str],
    ) -> Workspace:
        """Create a workspace and make it active."""
        workspace = Workspace(source, parameters)

        self._workspaces[workspace.id] = workspace
        self._active_workspace_id = workspace.id

        return workspace

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Return a workspace by ID."""
        if workspace_id not in self._workspaces:
            raise ValueError(
                f"Workspace '{workspace_id}' does not exist"
            )

        return self._workspaces[workspace_id]

    def select_workspace(self, workspace_id: str) -> None:
        """Select an existing workspace as active."""
        self.get_workspace(workspace_id)
        self._active_workspace_id = workspace_id

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace and update the active selection."""
        self.get_workspace(workspace_id)

        del self._workspaces[workspace_id]

        if self._active_workspace_id == workspace_id:
            self._active_workspace_id = next(
                iter(self._workspaces), None
            )