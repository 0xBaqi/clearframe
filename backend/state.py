"""Small JSON-backed state adapter for local development and tests.

It deliberately mirrors the eventual persistence boundary without adding a cloud
dependency.  The state is an administrative case record, never a legal opinion.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from backend.models import Operation, Status


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


class LocalProjectStore:
    """Persistent local project/case state; replace with DynamoDB later."""

    def __init__(self, path: Path, project_id: str = "night-shift"):
        self.path = path
        self.project_id = project_id

    def load(self) -> ProjectState:
        if not self.path.exists():
            return ProjectState(self.project_id)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        cases = {
            item_id: CaseState(
                item_id=value["item_id"], status=Status(value["status"]), paused=value.get("paused", False),
                evidence_ids=value.get("evidence_ids", []), requests=value.get("requests", []),
                human_decision=value.get("human_decision"),
            )
            for item_id, value in raw.get("cases", {}).items()
        }
        operations = [Operation(**operation) for operation in raw.get("operations", [])]
        return ProjectState(raw["project_id"], cases, operations, raw.get("received_evidence", []))

    def save(self, state: ProjectState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "project_id": state.project_id,
            "cases": {item_id: {**asdict(case), "status": case.status.value} for item_id, case in state.cases.items()},
            "operations": [asdict(operation) for operation in state.operations],
            "received_evidence": state.received_evidence,
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def append_operation(self, state: ProjectState, action: str, detail: str, evidence_id: str | None = None) -> Operation:
        operation = Operation(action, detail, evidence_id, sequence=len(state.operations) + 1)
        state.operations.append(operation)
        return operation
