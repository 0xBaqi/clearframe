from dataclasses import dataclass, field

from packages.core.types import Operation, Status


@dataclass
class CaseState:
    item_id: str
    status: Status
    paused: bool = False
    evidence_ids: list[str] = field(default_factory=list)
    requests: list[str] = field(default_factory=list)
    human_decision: str | None = None


@dataclass
class ProjectState:
    project_id: str
    cases: dict[str, CaseState] = field(default_factory=dict)
    operations: list[Operation] = field(default_factory=list)
    received_evidence: list[dict] = field(default_factory=list)
