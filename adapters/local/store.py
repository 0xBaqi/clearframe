"""JSON-backed local state adapter; cloud persistence belongs in a future adapter."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from packages.core.state import CaseState, ProjectState
from packages.core.types import Operation, Status


class LocalProjectStore:
    def __init__(self, path: Path, project_id: str = "night-shift"):
        self.path, self.project_id = path, project_id

    def load(self) -> ProjectState:
        if not self.path.exists():
            return ProjectState(self.project_id)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        cases = {item_id: CaseState(value["item_id"], Status(value["status"]), value.get("paused", False), value.get("evidence_ids", []), value.get("requests", []), value.get("human_decision")) for item_id, value in raw.get("cases", {}).items()}
        return ProjectState(raw["project_id"], cases, [Operation(**operation) for operation in raw.get("operations", [])], raw.get("received_evidence", []))

    def save(self, state: ProjectState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"project_id": state.project_id, "cases": {item_id: {**asdict(case), "status": case.status.value} for item_id, case in state.cases.items()}, "operations": [asdict(operation) for operation in state.operations], "received_evidence": state.received_evidence}
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def append_operation(self, state: ProjectState, action: str, detail: str, evidence_id: str | None = None) -> Operation:
        operation = Operation(action, detail, evidence_id, sequence=len(state.operations) + 1)
        state.operations.append(operation)
        return operation
