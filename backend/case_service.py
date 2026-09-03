"""Persistent, local clearance-case workflows.

All transitions are triggered by evidence inspection or an explicit human action.
The service records administrative operations; it never makes a legal conclusion.
"""
from __future__ import annotations

from dataclasses import asdict

from backend.evidence_tools import ClearanceTools, SeedEvidenceRepository
from backend.models import ClearanceItem, EvidenceRecord, ProjectIntent, Status
from backend.state import CaseState, LocalProjectStore


class ClearanceCaseService:
    def __init__(self, repository: SeedEvidenceRepository, intent: ProjectIntent, store: LocalProjectStore):
        self.repository = repository
        self.intent = intent
        self.store = store
        self.state = store.load()
        for record_data in self.state.received_evidence:
            record = EvidenceRecord(**record_data)
            if not any(existing.id == record.id for existing in self.repository.evidence):
                self.repository.evidence.append(record)
        self.tools = ClearanceTools(repository, self.state.operations)

    def _item(self, item_id: str) -> ClearanceItem:
        return next(item for item in self.repository.items if item.id == item_id)

    def _case(self, item_id: str, status: Status) -> CaseState:
        return self.state.cases.setdefault(item_id, CaseState(item_id, status))

    def _save(self) -> None:
        self.store.save(self.state)

    def operations_tape(self):
        """The persistent event feed consumed by the Operations Tape UI."""
        return list(self.state.operations)

    def create_daniel_request(self) -> CaseState:
        item = self._item("daniel")
        evidence = self.tools.find_evidence(item)
        if evidence:
            raise ValueError("A release is already present; inspect received evidence instead.")
        case = self._case(item.id, Status.EVIDENCE_MISSING)
        request_id = f"request-{item.id}-{len(case.requests) + 1}"
        case.requests.append(request_id)
        case.status = Status.AWAITING_RESPONSE
        self.store.append_operation(self.state, "create_document_request", f"Created appearance-release request for {item.name}.")
        self._save()
        return case

    def receive_daniel_release(self, record: EvidenceRecord) -> CaseState:
        if record.item_id != "daniel":
            raise ValueError("This workflow accepts Daniel Reed evidence only.")
        if not any(existing.id == record.id for existing in self.repository.evidence):
            self.repository.evidence.append(record)
        if not any(existing["id"] == record.id for existing in self.state.received_evidence):
            self.state.received_evidence.append(asdict(record))
        self.store.append_operation(self.state, "receive_evidence", f"Received {record.document_type} for Daniel Reed.", record.id)
        case = self._case("daniel", Status.AWAITING_RESPONSE)
        inspected = self.tools.read_permission_scope(record)
        case.evidence_ids.append(record.id)
        if inspected.signed is not True or inspected.dated is not True:
            case.status = Status.SIGNATURE_DEFICIENCY
            self.store.append_operation(self.state, "detect_signature_deficiency", "Release is missing a signature or date; correction is required.", record.id)
            request_id = f"correction-daniel-{len(case.requests) + 1}"
            case.requests.append(request_id)
            case.status = Status.AWAITING_RESPONSE
            self.store.append_operation(self.state, "request_correction", "Requested a signed and dated appearance release from Daniel Reed.", record.id)
            self._save()
            return case

        comparison = self.tools.compare_scope_to_intent(inspected, self.intent)
        case.status = Status.EVIDENCE_COMPLETE if comparison.matches else Status.SCOPE_MISMATCH
        self._save()
        return case

    def begin_painting_human_review(self) -> CaseState:
        item = self._item("painting")
        records = self.tools.find_evidence(item)
        case = self._case(item.id, Status.HUMAN_REVIEW)
        if not records:
            raise ValueError("Painting case has no evidence to escalate.")
        record = self.tools.read_permission_scope(records[0])
        if record.signed is True and record.dated is True:
            raise ValueError("Painting evidence no longer requires this escalation path.")
        reason = "The record cannot establish a rights holder or permission scope. Human review is required; no legal determination was made."
        self.tools.escalate_for_human_review(item, reason)
        case.status = Status.HUMAN_REVIEW
        case.paused = True
        self._save()
        return case

    def record_painting_human_decision(self, decision: str) -> CaseState:
        case = self._case("painting", Status.HUMAN_REVIEW)
        if not case.paused:
            raise ValueError("Painting case is not waiting for a human decision.")
        if not decision.strip():
            raise ValueError("A human decision is required to resume the case.")
        case.human_decision = decision.strip()
        self.store.append_operation(self.state, "record_human_decision", "Human decision recorded for Painting in Scene 7; no legal determination by agent.")
        case.paused = False
        case.status = Status.HUMAN_DECISION_RECORDED
        self.store.append_operation(self.state, "resume_case", "Painting case resumed after human decision.")
        self._save()
        return case
