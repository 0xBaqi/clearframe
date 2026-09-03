from typing import Protocol

from packages.core.state.models import ProjectState
from packages.core.types import Operation


class ProjectStore(Protocol):
    """Persistence port for project/case state and its operations tape."""

    def load(self) -> ProjectState: ...
    def save(self, state: ProjectState) -> None: ...
    def append_operation(self, state: ProjectState, action: str, detail: str, evidence_id: str | None = None) -> Operation: ...
