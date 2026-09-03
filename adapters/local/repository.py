from packages.core.types import ClearanceItem, EvidenceRecord


class LocalEvidenceRepository:
    """In-memory demo adapter; replace it without changing core rules."""

    def __init__(self, items: list[ClearanceItem], evidence: list[EvidenceRecord]):
        self.items = items
        self.evidence = evidence

    def list_clearance_items(self) -> list[ClearanceItem]:
        return self.items

    def find_evidence(self, item_id: str) -> list[EvidenceRecord]:
        return [record for record in self.evidence if record.item_id == item_id]

    def add_evidence(self, record: EvidenceRecord) -> None:
        self.evidence.append(record)
