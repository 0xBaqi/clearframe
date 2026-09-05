"""Provider-neutral action contracts."""
from dataclasses import dataclass
from typing import Protocol

from packages.core.types import ClearanceResult, ProjectIntent


class AgentProvider(Protocol):
    """Product callers never import a model SDK."""
    def run(self, intent: ProjectIntent) -> list[ClearanceResult]: ...


@dataclass(frozen=True)
class AgentActionRequest:
    id: str
    action: str
    item_id: str
    reason: str
    evidence_id: str | None = None


@dataclass(frozen=True)
class AgentActionResult:
    request_id: str
    accepted: bool
    delivery_id: str | None = None
    detail: str = ""


class AgentActionExecutor(Protocol):
    def execute(self, request: AgentActionRequest) -> AgentActionResult: ...
