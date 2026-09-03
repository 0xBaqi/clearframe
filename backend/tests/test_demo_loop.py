import tempfile
import unittest
from pathlib import Path
from demo.night_shift.run_agent_demo import build, daniel_release, run_demo
from packages.core.types import EventActor, EventType, Status

class DemoLoopTests(unittest.TestCase):
    def test_complete_demo_has_four_expected_final_states(self):
        state = run_demo()
        self.assertEqual(state.cases["sarah"].status, Status.EVIDENCE_COMPLETE)
        self.assertEqual(state.cases["daniel"].status, Status.EVIDENCE_COMPLETE)
        self.assertEqual(state.cases["archive"].status, Status.SCOPE_MISMATCH)
        self.assertEqual(state.cases["painting"].status, Status.HUMAN_DECISION_RECORDED)
    def test_daniel_waits_and_resumes_from_persisted_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"; provider, service = build(path)
            provider.start_night_shift(); self.assertTrue(service.workflow.state.cases["daniel"].paused)
            service.receive_document(daniel_release("unsigned", False)); self.assertTrue(service.workflow.state.cases["daniel"].paused)
            provider, service = build(path); service.receive_document(daniel_release("signed", True))
            self.assertEqual(service.workflow.state.cases["daniel"].status, Status.EVIDENCE_COMPLETE)
    def test_tape_is_event_derived_and_human_gate_is_recorded(self):
        state = run_demo()
        self.assertTrue(all(event.recorded_at and event.sequence for event in state.events))
        painting = [event for event in state.events if event.item_id == "painting"]
        self.assertEqual([event.event_type for event in painting][-3:], [EventType.HUMAN_REVIEW_REQUESTED, EventType.HUMAN_DECISION_RECORDED, EventType.CASE_RESUMED])
        self.assertEqual(painting[-2].actor, EventActor.HUMAN)
if __name__ == "__main__": unittest.main()
