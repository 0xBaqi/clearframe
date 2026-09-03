"""JSON-backed local state adapter; cloud persistence belongs in a future adapter."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from packages.core.state import CaseState, ProjectState
from packages.core.types import DomainEvent, EventType, Status


class LocalProjectStore:
    def __init__(self, path: Path, project_id: str = "night-shift"):
        self.path, self.project_id = path, project_id

    def load(self) -> ProjectState:
        if not self.path.exists():
            return ProjectState(self.project_id)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        cases = {item_id: CaseState(value["item_id"], Status(value["status"]), value.get("paused", False), value.get("evidence_ids", []), value.get("requests", []), value.get("human_decision")) for item_id, value in raw.get("cases", {}).items()}
        events = [DomainEvent(EventType(event["event_type"]), event["item_id"], event["detail"], event.get("evidence_id"), event.get("sequence")) for event in raw.get("events", [])]
        return ProjectState(raw["project_id"], cases, events, raw.get("received_evidence", []))

    def save(self, state: ProjectState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"project_id": state.project_id, "cases": {item_id: {**asdict(case), "status": case.status.value} for item_id, case in state.cases.items()}, "events": [asdict(event) for event in state.events], "received_evidence": state.received_evidence}
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def append_event(self, state: ProjectState, event_type: EventType, item_id: str, detail: str, evidence_id: str | None = None) -> DomainEvent:
        event = DomainEvent(event_type, item_id, detail, evidence_id, sequence=len(state.events) + 1)
        state.events.append(event)
        return event
