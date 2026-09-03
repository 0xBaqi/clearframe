"""Compatibility entry point; workflow rules live in packages.core.clearance."""
from packages.core.clearance.workflows import ClearanceCaseWorkflow
from packages.core.types import EvidenceRecord


class ClearanceCaseService(ClearanceCaseWorkflow):
    def create_daniel_request(self):
        return self.create_document_request("daniel")

    def receive_daniel_release(self, record: EvidenceRecord):
        if record.item_id != "daniel":
            raise ValueError("This compatibility workflow accepts Daniel Reed evidence only.")
        return self.receive_evidence(record)

    def begin_painting_human_review(self):
        return self.begin_human_review("painting")

    def record_painting_human_decision(self, decision: str):
        return self.record_human_decision("painting", decision)
