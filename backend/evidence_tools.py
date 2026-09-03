from __future__ import annotations

from dataclasses import dataclass

from backend.models import ClearanceItem, EvidenceRecord, Operation, ProjectIntent


@dataclass
class ScopeComparison:
    matches: bool
    reasons: list[str]


class SeedEvidenceRepository:
    """Replace this adapter with S3/DynamoDB repositories in later milestones."""

    def __init__(self, items: list[ClearanceItem], evidence: list[EvidenceRecord]):
        self.items = items
        self.evidence = evidence

    def list_clearance_items(self) -> list[ClearanceItem]:
        return self.items

    def find_evidence(self, item_id: str) -> list[EvidenceRecord]:
        return [record for record in self.evidence if record.item_id == item_id]


class ClearanceTools:
    def __init__(self, repository: SeedEvidenceRepository, operations: list[Operation] | None = None):
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
        reasons: list[str] = []
        if record.distribution is None or record.territories is None:
            reasons.append("The record does not provide a usable permission scope.")
        else:
            missing_distribution = sorted(set(intent.distribution) - set(record.distribution))
            if missing_distribution:
                reasons.append("Distribution excludes: " + ", ".join(missing_distribution) + ".")
            if "Worldwide" in intent.territories and "Worldwide" not in record.territories:
                reasons.append("Territory is limited to: " + ", ".join(record.territories) + ".")
        if intent.end_date and record.expires_on and record.expires_on < intent.end_date:
            reasons.append(f"Permission expires on {record.expires_on} before the project end date.")
        self._record("compare_scope_to_intent", "; ".join(reasons) or "Scope supports declared intent.", record.id)
        return ScopeComparison(matches=not reasons, reasons=reasons)

    def escalate_for_human_review(self, item: ClearanceItem, reason: str) -> None:
        self._record("escalate_for_human_review", f"Escalated {item.name}: {reason}")
