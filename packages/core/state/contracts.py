from typing import Protocol

from packages.core.state.models import ProjectState
from packages.core.types import DomainEvent, EventType


class ProjectStore(Protocol):
    """Persistence port for project/case state and its event-sourced tape."""
    def load(self) -> ProjectState: ...
    def save(self, state: ProjectState) -> None: ...
    def append_event(self, state: ProjectState, event_type: EventType, item_id: str, detail: str, evidence_id: str | None = None) -> DomainEvent: ...
