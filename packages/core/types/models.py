from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum


class Status(StrEnum):
    EVIDENCE_COMPLETE = "EVIDENCE_COMPLETE"; EVIDENCE_MISSING = "EVIDENCE_MISSING"; SCOPE_MISMATCH = "SCOPE_MISMATCH"; HUMAN_REVIEW = "HUMAN_REVIEW"; AWAITING_RESPONSE = "AWAITING_RESPONSE"; SIGNATURE_DEFICIENCY = "SIGNATURE_DEFICIENCY"; HUMAN_DECISION_RECORDED = "HUMAN_DECISION_RECORDED"

class EventType(StrEnum):
    PROJECT_SCAN_STARTED = "PROJECT_SCAN_STARTED"; CLEARANCE_ITEM_IDENTIFIED = "CLEARANCE_ITEM_IDENTIFIED"; EVIDENCE_MATCHED = "EVIDENCE_MATCHED"; EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"; DOCUMENT_RECEIVED = "DOCUMENT_RECEIVED"; DOCUMENT_DEFICIENCY_FOUND = "DOCUMENT_DEFICIENCY_FOUND"; CORRECTION_REQUESTED = "CORRECTION_REQUESTED"; SCOPE_MISMATCH_DETECTED = "SCOPE_MISMATCH_DETECTED"; HUMAN_REVIEW_REQUESTED = "HUMAN_REVIEW_REQUESTED"; HUMAN_DECISION_RECORDED = "HUMAN_DECISION_RECORDED"; CASE_RESUMED = "CASE_RESUMED"; ITEM_EVIDENCE_COMPLETE = "ITEM_EVIDENCE_COMPLETE"

class EventActor(StrEnum):
    AGENT = "AGENT"; HUMAN = "HUMAN"; SYSTEM = "SYSTEM"; EXTERNAL = "EXTERNAL"

@dataclass(frozen=True)
class ProjectIntent: distribution: list[str]; territories: list[str]; end_date: str | None = None
@dataclass(frozen=True)
class ClearanceItem: id: str; name: str; category: str; scene: str
@dataclass(frozen=True)
class EvidenceRecord:
    id: str; item_id: str; document_type: str; signed: bool | None; dated: bool | None; distribution: list[str] | None; territories: list[str] | None; expires_on: str | None; extract_confidence: str; notes: str
@dataclass
class Operation: action: str; detail: str; evidence_id: str | None = None; sequence: int | None = None
@dataclass(frozen=True)
class DomainEvent:
    event_type: EventType; item_id: str; detail: str; evidence_id: str | None = None; sequence: int | None = None; actor: EventActor = EventActor.SYSTEM; recorded_at: str = ""
@dataclass
class ClearanceResult:
    item: ClearanceItem; status: Status; explanation: str; evidence_chain: list[str]; operations: list[Operation] = field(default_factory=list)
    def as_dict(self) -> dict: return {"item": asdict(self.item), "status": self.status.value, "explanation": self.explanation, "evidence_chain": self.evidence_chain, "operations": [asdict(event) for event in self.operations]}
