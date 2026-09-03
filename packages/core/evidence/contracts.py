from typing import Protocol

from packages.core.types import ClearanceItem, EvidenceRecord


class EvidenceRepository(Protocol):
    """Product-facing evidence port; storage and extraction are adapter concerns."""

    def list_clearance_items(self) -> list[ClearanceItem]: ...
    def find_evidence(self, item_id: str) -> list[EvidenceRecord]: ...
    def add_evidence(self, record: EvidenceRecord) -> None: ...
