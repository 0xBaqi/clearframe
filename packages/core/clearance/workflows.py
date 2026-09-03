from dataclasses import asdict

from packages.core.clearance.engine import EvidenceTools
from packages.core.evidence import EvidenceRepository
from packages.core.state import CaseState, ProjectStore, ProjectState
from packages.core.types import ClearanceItem, DomainEvent, EventType, EvidenceRecord, ProjectIntent, Status


class ClearanceCaseWorkflow:
    """Provider-independent administrative case transitions and event recording."""

    def __init__(self, repository: EvidenceRepository, intent: ProjectIntent, store: ProjectStore):
        self.repository, self.intent, self.store = repository, intent, store
        self.state: ProjectState = store.load()
        for record_data in self.state.received_evidence:
            record = EvidenceRecord(**record_data)
            if not any(existing.id == record.id for existing in repository.find_evidence(record.item_id)):
                repository.add_evidence(record)
        self.tools = EvidenceTools(repository)

    def _item(self, item_id: str) -> ClearanceItem:
        return next(item for item in self.repository.list_clearance_items() if item.id == item_id)

    def _case(self, item_id: str, status: Status) -> CaseState:
        return self.state.cases.setdefault(item_id, CaseState(item_id, status))

    def _event(self, event_type: EventType, item_id: str, detail: str, evidence_id: str | None = None) -> DomainEvent:
        return self.store.append_event(self.state, event_type, item_id, detail, evidence_id)

    def _start_item(self, item: ClearanceItem) -> None:
        self._event(EventType.PROJECT_SCAN_STARTED, item.id, "Project scan started.")
        self._event(EventType.CLEARANCE_ITEM_IDENTIFIED, item.id, f"Clearance item identified: {item.name}.")

    def _save(self) -> None:
        self.store.save(self.state)

    def operations_tape(self) -> list[DomainEvent]:
        return list(self.state.events)

    def create_document_request(self, item_id: str) -> CaseState:
        item = self._item(item_id)
        self._start_item(item)
        evidence = self.tools.find_evidence(item)
        if evidence:
            raise ValueError("Evidence is already present; inspect received evidence instead.")
        case = self._case(item.id, Status.EVIDENCE_MISSING)
        request_id = f"request-{item.id}-{len(case.requests) + 1}"
        case.requests.append(request_id)
        case.status = Status.AWAITING_RESPONSE
        self._event(EventType.EVIDENCE_REQUESTED, item.id, f"Evidence requested for {item.name}.")
        self._save()
        return case

    def receive_evidence(self, record: EvidenceRecord) -> CaseState:
        item = self._item(record.item_id)
        if not any(existing.id == record.id for existing in self.repository.find_evidence(record.item_id)):
            self.repository.add_evidence(record)
        if not any(existing["id"] == record.id for existing in self.state.received_evidence):
            self.state.received_evidence.append(asdict(record))
        self._event(EventType.DOCUMENT_RECEIVED, item.id, f"Document received: {record.document_type}.", record.id)
        case = self._case(item.id, Status.AWAITING_RESPONSE)
        inspected = self.tools.read_permission_scope(record)
        case.evidence_ids.append(record.id)
        if inspected.signed is not True or inspected.dated is not True:
            self._event(EventType.DOCUMENT_DEFICIENCY_FOUND, item.id, "Record is missing a signature or date.", record.id)
            request_id = f"correction-{item.id}-{len(case.requests) + 1}"
            case.requests.append(request_id)
            case.status = Status.AWAITING_RESPONSE
            self._event(EventType.CORRECTION_REQUESTED, item.id, f"Correction requested for {item.name}.", record.id)
            self._save()
            return case
        self._event(EventType.EVIDENCE_MATCHED, item.id, "Submitted evidence matched to the clearance item.", record.id)
        comparison = self.tools.compare_scope_to_intent(inspected, self.intent)
        if comparison.matches:
            case.status = Status.EVIDENCE_COMPLETE
            self._event(EventType.ITEM_EVIDENCE_COMPLETE, item.id, "Evidence supports the declared project intent.", record.id)
        else:
            case.status = Status.SCOPE_MISMATCH
            self._event(EventType.SCOPE_MISMATCH_DETECTED, item.id, "; ".join(comparison.reasons), record.id)
        self._save()
        return case

    def begin_human_review(self, item_id: str) -> CaseState:
        item = self._item(item_id)
        self._start_item(item)
        records = self.tools.find_evidence(item)
        if not records:
            raise ValueError("Case has no evidence to escalate.")
        record = self.tools.read_permission_scope(records[0])
        if record.signed is True and record.dated is True:
            raise ValueError("Evidence no longer requires this escalation path.")
        case = self._case(item.id, Status.HUMAN_REVIEW)
        case.status, case.paused = Status.HUMAN_REVIEW, True
        self._event(EventType.HUMAN_REVIEW_REQUESTED, item.id, "Human review requested; no legal determination was made.", record.id)
        self._save()
        return case

    def record_human_decision(self, item_id: str, decision: str) -> CaseState:
        case = self._case(item_id, Status.HUMAN_REVIEW)
        if not case.paused:
            raise ValueError("Case is not waiting for a human decision.")
        if not decision.strip():
            raise ValueError("A human decision is required to resume the case.")
        case.human_decision = decision.strip()
        self._event(EventType.HUMAN_DECISION_RECORDED, item_id, "Human decision recorded; no legal determination by agent.")
        case.paused, case.status = False, Status.HUMAN_DECISION_RECORDED
        self._event(EventType.CASE_RESUMED, item_id, "Case resumed after human decision.")
        self._save()
        return case
