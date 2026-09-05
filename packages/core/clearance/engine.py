from packages.core.evidence import EvidenceRepository, ScopeComparison, compare_scope_to_intent
from packages.core.types import ClearanceItem, ClearanceResult, EvidenceRecord, Operation, ProjectIntent, Status


class EvidenceTools:
    """Named product operations. An agent provider may orchestrate them, not alter their facts."""

    def __init__(self, repository: EvidenceRepository, operations: list[Operation] | None = None):
        self.repository = repository
        self.operations = operations if operations is not None else []

    def _record(self, action: str, detail: str, evidence_id: str | None = None) -> None:
        self.operations.append(Operation(action, detail, evidence_id, sequence=len(self.operations) + 1))

    def list_clearance_items(self) -> list[ClearanceItem]:
        items = self.repository.list_clearance_items()
        self._record("list_clearance_items", f"Loaded {len(items)} clearance items.")
        return items

    def find_evidence(self, item: ClearanceItem) -> list[EvidenceRecord]:
        evidence = self.repository.find_evidence(item.id)
        self._record("find_evidence", f"Found {len(evidence)} record(s) for {item.name}.")
        return evidence

    def read_permission_scope(self, record: EvidenceRecord) -> EvidenceRecord:
        self._record("read_permission_scope", f"Read administrative fields from {record.document_type}.", record.id)
        return record

    def compare_scope_to_intent(self, record: EvidenceRecord, intent: ProjectIntent) -> ScopeComparison:
        comparison = compare_scope_to_intent(record, intent)
        self._record("compare_scope_to_intent", "; ".join(comparison.reasons) or "Scope supports declared intent.", record.id)
        return comparison

    def escalate_for_human_review(self, item: ClearanceItem, reason: str) -> None:
        self._record("escalate_for_human_review", f"Escalated {item.name}: {reason}")


class ClearanceEngine:
    """Provider-independent clearance evaluation and status rules."""

    def __init__(self, repository: EvidenceRepository):
        self.tools = EvidenceTools(repository)

    def run(self, intent: ProjectIntent) -> list[ClearanceResult]:
        results: list[ClearanceResult] = []
        for item in self.tools.list_clearance_items():
            start = len(self.tools.operations)
            evidence = self.tools.find_evidence(item)
            if not evidence:
                results.append(ClearanceResult(item, Status.EVIDENCE_MISSING, "No submitted evidence record was found.", [item.name], self.tools.operations[start:]))
                continue
            record = self.tools.read_permission_scope(evidence[0])
            chain = [item.name, f"{record.document_type} ({record.id})"]
            if record.signed is not True or record.dated is not True:
                reason = "The submitted record is incomplete: signature and date are required administrative fields."
                self.tools.escalate_for_human_review(item, reason)
                results.append(ClearanceResult(item, Status.HUMAN_REVIEW, reason, chain, self.tools.operations[start:]))
                continue
            comparison = self.tools.compare_scope_to_intent(record, intent)
            chain.append("Project intent comparison")
            if comparison.matches:
                results.append(ClearanceResult(item, Status.EVIDENCE_COMPLETE, "Submitted evidence has complete administrative fields and supports the declared intent.", chain, self.tools.operations[start:]))
            else:
                results.append(ClearanceResult(item, Status.SCOPE_MISMATCH, " ".join(comparison.reasons), chain, self.tools.operations[start:]))
        return results
