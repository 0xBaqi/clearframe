import unittest

from backend.agent import StrandsClearanceAgent
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository


class NightShiftAgentTests(unittest.TestCase):
    def setUp(self):
        self.results = StrandsClearanceAgent(night_shift_repository()).run(NIGHT_SHIFT_INTENT)
        self.by_name = {result.item.name: result for result in self.results}

    def test_seeded_project_produces_expected_operational_statuses(self):
        self.assertEqual(self.by_name["Sarah Cole"].status, "EVIDENCE_COMPLETE")
        self.assertEqual(self.by_name["Daniel Reed"].status, "EVIDENCE_MISSING")
        self.assertEqual(self.by_name["News Clip #03"].status, "SCOPE_MISMATCH")
        self.assertEqual(self.by_name["Painting in Scene 7"].status, "HUMAN_REVIEW")

    def test_statuses_are_supported_by_tool_operations(self):
        archive_actions = [event.action for event in self.by_name["News Clip #03"].operations]
        painting_actions = [event.action for event in self.by_name["Painting in Scene 7"].operations]
        self.assertIn("read_permission_scope", archive_actions)
        self.assertIn("compare_scope_to_intent", archive_actions)
        self.assertIn("escalate_for_human_review", painting_actions)

    def test_changing_scope_changes_outcome(self):
        repository = night_shift_repository()
        archive = next(record for record in repository.evidence if record.item_id == "archive")
        replacement = archive.__class__(archive.id, archive.item_id, archive.document_type, True, True, list(NIGHT_SHIFT_INTENT.distribution), ["Worldwide"], "2030-01-01", archive.extract_confidence, archive.notes)
        repository.evidence[repository.evidence.index(archive)] = replacement
        results = StrandsClearanceAgent(repository).run(NIGHT_SHIFT_INTENT)
        archive_result = next(result for result in results if result.item.id == "archive")
        self.assertEqual(archive_result.status, "EVIDENCE_COMPLETE")


if __name__ == "__main__":
    unittest.main()
