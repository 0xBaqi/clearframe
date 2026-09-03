import tempfile
import unittest
from pathlib import Path

from adapters.local import LocalInbox, LocalProjectStore
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from packages.agent_contract import AgentActionRequest, AgentActionResult
from packages.core.clearance import ClearanceCaseWorkflow
from packages.core.types import EventType, EvidenceRecord, Status
from services.agent import ClearanceApplicationService


def daniel_release(record_id: str, signed: bool) -> EvidenceRecord:
    return EvidenceRecord(record_id, "daniel", "appearance release", signed, True, list(NIGHT_SHIFT_INTENT.distribution), ["Worldwide"], "2030-01-01", "high", "Fictional Daniel Reed release.")


class MilestoneTwoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = LocalProjectStore(Path(self.temp.name) / "night-shift.json")
        self.inbox = LocalInbox()
        self.workflow = ClearanceCaseWorkflow(night_shift_repository(), NIGHT_SHIFT_INTENT, self.store)
        self.service = ClearanceApplicationService(self.workflow, self.inbox)

    def tearDown(self):
        self.temp.cleanup()

    def test_action_request_and_result_contracts(self):
        request = AgentActionRequest("request-daniel-1", "REQUEST_EVIDENCE", "daniel", "No record found.")
        result = self.inbox.execute(request)
        self.assertEqual(result, AgentActionResult("request-daniel-1", True, "local-inbox-1", "Delivered to the controlled local inbox."))

    def test_daniel_workflow_event_order_and_actions(self):
        self.assertEqual(self.service.request_evidence("daniel").status, Status.AWAITING_RESPONSE)
        self.assertEqual(self.service.receive_document(daniel_release("unsigned", False)).status, Status.AWAITING_RESPONSE)
        self.assertEqual(self.service.receive_document(daniel_release("signed", True)).status, Status.EVIDENCE_COMPLETE)
        self.assertEqual([event.event_type for event in self.workflow.operations_tape()], [
            EventType.PROJECT_SCAN_STARTED, EventType.CLEARANCE_ITEM_IDENTIFIED, EventType.EVIDENCE_REQUESTED,
            EventType.DOCUMENT_RECEIVED, EventType.DOCUMENT_DEFICIENCY_FOUND, EventType.CORRECTION_REQUESTED,
            EventType.DOCUMENT_RECEIVED, EventType.EVIDENCE_MATCHED, EventType.ITEM_EVIDENCE_COMPLETE,
        ])
        self.assertEqual([delivery.action for delivery in self.inbox.deliveries], ["REQUEST_EVIDENCE", "REQUEST_CORRECTION"])

    def test_painting_pauses_and_resumes_with_events(self):
        paused = self.service.request_human_review("painting")
        self.assertTrue(paused.paused)
        resumed = self.service.record_human_decision("painting", "Artwork will be removed from the final cut.")
        self.assertFalse(resumed.paused)
        self.assertEqual([event.event_type for event in self.workflow.operations_tape()][-3:], [EventType.HUMAN_REVIEW_REQUESTED, EventType.HUMAN_DECISION_RECORDED, EventType.CASE_RESUMED])
        self.assertNotIn(EventType.SCOPE_MISMATCH_DETECTED, [event.event_type for event in self.workflow.operations_tape()])

    def test_operations_tape_is_recorded_event_source(self):
        self.service.request_evidence("daniel")
        tape = self.workflow.operations_tape()
        self.assertEqual(tape, self.workflow.state.events)
        self.assertTrue(all(isinstance(event.event_type, EventType) for event in tape))

    def test_scope_mismatch_is_evidence_derived(self):
        archive = next(record for record in night_shift_repository().evidence if record.item_id == "archive")
        case = self.service.receive_document(archive)
        self.assertEqual(case.status, Status.SCOPE_MISMATCH)
        self.assertEqual(self.workflow.operations_tape()[-1].event_type, EventType.SCOPE_MISMATCH_DETECTED)

    def test_core_has_no_provider_dependency(self):
        core = Path(__file__).resolve().parents[2] / "packages" / "core"
        forbidden = ("strands", "bedrock", "boto", "gemini", "nebius", "aws")
        text = "\n".join(path.read_text(encoding="utf-8").lower() for path in core.rglob("*.py"))
        self.assertFalse(any(token in text for token in forbidden))


if __name__ == "__main__":
    unittest.main()
