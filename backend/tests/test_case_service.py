import tempfile
import unittest
from pathlib import Path

from backend.case_service import ClearanceCaseService
from backend.models import EvidenceRecord, Status
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from backend.state import LocalProjectStore


def daniel_release(record_id: str, signed: bool) -> EvidenceRecord:
    return EvidenceRecord(
        record_id, "daniel", "appearance release", signed, True,
        ["YouTube", "Streaming platforms", "Film festivals"], ["Worldwide"], "2030-01-01", "high",
        "Fictional Daniel Reed release.",
    )


class PersistentCaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.store = LocalProjectStore(Path(self.temporary_directory.name) / "night-shift.json")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def service(self) -> ClearanceCaseService:
        return ClearanceCaseService(night_shift_repository(), NIGHT_SHIFT_INTENT, self.store)

    def test_daniel_evidence_resolution_is_tool_derived_and_persistent(self):
        service = self.service()
        initial = service.create_daniel_request()
        self.assertEqual(initial.status, Status.AWAITING_RESPONSE)

        after_unsigned = service.receive_daniel_release(daniel_release("daniel-unsigned", signed=False))
        self.assertEqual(after_unsigned.status, Status.AWAITING_RESPONSE)
        self.assertEqual(after_unsigned.requests, ["request-daniel-1", "correction-daniel-2"])

        resumed_service = self.service()
        completed = resumed_service.receive_daniel_release(daniel_release("daniel-signed", signed=True))
        self.assertEqual(completed.status, Status.EVIDENCE_COMPLETE)
        self.assertIn("daniel-unsigned", completed.evidence_ids)
        self.assertIn("daniel-signed", completed.evidence_ids)

        actions = [event.action for event in resumed_service.operations_tape()]
        self.assertEqual(actions, [
            "find_evidence", "create_document_request", "receive_evidence", "read_permission_scope",
            "detect_signature_deficiency", "request_correction", "receive_evidence", "read_permission_scope",
            "compare_scope_to_intent",
        ])
        self.assertTrue(self.store.path.exists())

    def test_painting_pauses_for_human_and_resumes_without_legal_conclusion(self):
        service = self.service()
        paused = service.begin_painting_human_review()
        self.assertEqual(paused.status, Status.HUMAN_REVIEW)
        self.assertTrue(paused.paused)

        resumed_service = self.service()
        resumed = resumed_service.record_painting_human_decision("Artwork will be removed from the final cut.")
        self.assertEqual(resumed.status, Status.HUMAN_DECISION_RECORDED)
        self.assertFalse(resumed.paused)
        self.assertEqual(resumed.human_decision, "Artwork will be removed from the final cut.")

        actions = [event.action for event in resumed_service.operations_tape()]
        self.assertEqual(actions, [
            "find_evidence", "read_permission_scope", "escalate_for_human_review",
            "record_human_decision", "resume_case",
        ])
        self.assertNotIn("compare_scope_to_intent", actions)

    def test_human_decision_is_required_before_painting_can_resume(self):
        service = self.service()
        service.begin_painting_human_review()
        with self.assertRaises(ValueError):
            service.record_painting_human_decision(" ")


if __name__ == "__main__":
    unittest.main()
