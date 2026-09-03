from dataclasses import asdict

from packages.core.clearance.engine import EvidenceTools
from packages.core.evidence import EvidenceRepository
from packages.core.state import CaseState, ProjectStore, ProjectState
from packages.core.types import ClearanceItem, EvidenceRecord, ProjectIntent, Status


class ClearanceCaseWorkflow:
    """Provider-independent administrative case transitions and operations."""

    def __init__(self, repository: EvidenceRepository, intent: ProjectIntent, store: ProjectStore):
        self.repository, self.intent, self.store = repository, intent, store
        self.state: ProjectState = store.load()
        for record_data in self.state.received_evidence:
            record = EvidenceRecord(**record_data)
            if not any(existing.id == record.id for existing in repository.find_evidence(record.item_id)):
                repository.add_evidence(record)
        self.tools = EvidenceTools(repository, self.state.operations)

    def _item(self, item_id: str) -> ClearanceItem:
        return next(item for item in self.repository.list_clearance_items() if item.id == item_id)

    def _case(self, item_id: str, status: Status) -> CaseState:
        return self.state.cases.setdefault(item_id, CaseState(item_id, status))

    def _save(self) -> None:
        self.store.save(self.state)

    def operations_tape(self):
        return list(self.state.operations)

    def create_document_request(self, item_id: str) -> CaseState:
        item = self._item(item_id)
        evidence = self.tools.find_evidence(item)
        if evidence:
            raise ValueError("Evidence is already present; inspect received evidence instead.")
        case = self._case(item.id, Status.EVIDENCE_MISSING)
        request_id = f"request-{item.id}-{len(case.requests) + 1}"
        case.requests.append(request_id)
        case.status = Status.AWAITING_RESPONSE
        self.store.append_operation(self.state, "create_document_request", f"Created evidence request for {item.name}.")
        self._save()
        return case

    def receive_evidence(self, record: EvidenceRecord) -> CaseState:
        item = self._item(record.item_id)
        if not any(existing.id == record.id for existing in self.repository.find_evidence(record.item_id)):
            self.repository.add_evidence(record)
        if not any(existing["id"] == record.id for existing in self.state.received_evidence):
            self.state.received_evidence.append(asdict(record))
        self.store.append_operation(self.state, "receive_evidence", f"Received {record.document_type} for {item.name}.", record.id)
        case = self._case(item.id, Status.AWAITING_RESPONSE)
        inspected = self.tools.read_permission_scope(record)
        case.evidence_ids.append(record.id)
        if inspected.signed is not True or inspected.dated is not True:
            case.status = Status.SIGNATURE_DEFICIENCY
            self.store.append_operation(self.state, "detect_signature_deficiency", "Record is missing a signature or date; correction is required.", record.id)
            request_id = f"correction-{item.id}-{len(case.requests) + 1}"
            case.requests.append(request_id)
            case.status = Status.AWAITING_RESPONSE
            self.store.append_operation(self.state, "request_correction", f"Requested a signed and dated record for {item.name}.", record.id)
            self._save()
            return case
        comparison = self.tools.compare_scope_to_intent(inspected, self.intent)
        case.status = Status.EVIDENCE_COMPLETE if comparison.matches else Status.SCOPE_MISMATCH
        self._save()
        return case

    def begin_human_review(self, item_id: str) -> CaseState:
        item = self._item(item_id)
        records = self.tools.find_evidence(item)
        if not records:
            raise ValueError("Case has no evidence to escalate.")
        record = self.tools.read_permission_scope(records[0])
        if record.signed is True and record.dated is True:
            raise ValueError("Evidence no longer requires this escalation path.")
        case = self._case(item.id, Status.HUMAN_REVIEW)
        reason = "The record cannot establish a rights holder or permission scope. Human review is required; no legal determination was made."
        self.tools.escalate_for_human_review(item, reason)
        case.status, case.paused = Status.HUMAN_REVIEW, True
        self._save()
        return case

    def record_human_decision(self, item_id: str, decision: str) -> CaseState:
        case = self._case(item_id, Status.HUMAN_REVIEW)
        if not case.paused:
            raise ValueError("Case is not waiting for a human decision.")
        if not decision.strip():
            raise ValueError("A human decision is required to resume the case.")
        case.human_decision = decision.strip()
        self.store.append_operation(self.state, "record_human_decision", f"Human decision recorded for {item_id}; no legal determination by agent.")
        case.paused, case.status = False, Status.HUMAN_DECISION_RECORDED
        self.store.append_operation(self.state, "resume_case", f"Case {item_id} resumed after human decision.")
        self._save()
        return case
