from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

from backend.case_service import ClearanceCaseService
from backend.models import EvidenceRecord, Status
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from backend.state import LocalProjectStore
from packages.core.types import EventType


def daniel_release(record_id: str, signed: bool) -> EvidenceRecord:
    return EvidenceRecord(record_id, "daniel", "appearance release", signed, True, list(NIGHT_SHIFT_INTENT.distribution), ["Worldwide"], "2030-01-01", "high", "Fictional Daniel Reed release.")


class PersistentCaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.store = LocalProjectStore(Path(self.temporary_directory.name) / "night-shift.json")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def service(self) -> ClearanceCaseService:
        return ClearanceCaseService(night_shift_repository(), NIGHT_SHIFT_INTENT, self.store)

    def test_daniel_evidence_resolution_is_persistent(self):
        service = self.service()
        self.assertEqual(service.create_daniel_request().status, Status.AWAITING_RESPONSE)
        self.assertEqual(service.receive_daniel_release(daniel_release("daniel-unsigned", False)).status, Status.AWAITING_RESPONSE)
        resumed = self.service()
        completed = resumed.receive_daniel_release(daniel_release("daniel-signed", True))
        self.assertEqual(completed.status, Status.EVIDENCE_COMPLETE)
        self.assertIn("daniel-signed", completed.evidence_ids)
        self.assertEqual(resumed.operations_tape()[-1].event_type, EventType.ITEM_EVIDENCE_COMPLETE)

    def test_painting_pauses_and_resumes(self):
        service = self.service()
        self.assertTrue(service.begin_painting_human_review().paused)
        self.assertFalse(service.record_painting_human_decision("Remove artwork.").paused)

    def test_incoming_evidence_preserves_human_gate_until_decision(self):
        for signed, territories in ((True, ["Worldwide"]), (False, ["Worldwide"]), (True, ["US"])):
            with self.subTest(signed=signed, territories=territories):
                service = self.service()
                service.begin_painting_human_review()
                record = replace(daniel_release(f"painting-{signed}-{territories[0]}", signed), item_id="painting", territories=territories)
                before = len(service.operations_tape())
                service.receive_evidence(record)
                restored = self.service()
                case = restored.state.cases["painting"]
                self.assertEqual(case.status, Status.HUMAN_REVIEW)
                self.assertTrue(case.paused)
                self.assertIsNone(case.human_decision)
                self.assertIn(record.id, case.evidence_ids)
                self.assertTrue(any(r["id"] == record.id for r in restored.state.received_evidence))
                self.assertEqual([e.event_type for e in restored.operations_tape()[before:]], [EventType.DOCUMENT_RECEIVED])
        restored.record_painting_human_decision("Permission reviewed by a human.")
        self.assertFalse(self.service().state.cases["painting"].paused)
        completed = restored.receive_evidence(replace(record, id="painting-after-review", signed=True, territories=["Worldwide"]))
        self.assertEqual(completed.status, Status.EVIDENCE_COMPLETE)
        self.assertIsNotNone(completed.human_decision)


if __name__ == "__main__":
    unittest.main()
