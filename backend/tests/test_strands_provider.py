import tempfile
import unittest
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from adapters.local import DeterministicProvider, LocalInbox, LocalProjectStore
from adapters.strands import StrandsConfig, StrandsProvider
from adapters.strands.provider import ProviderExecutionError, SYSTEM_PROMPT
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from packages.agent_contract import AgentActionRequest
from packages.core.clearance import ClearanceCaseWorkflow
from services.agent import ClearanceApplicationService
from adapters.strands.tools import build_strands_tools
from packages.core.types import EventType


class FakeAgent:
    def __init__(self):
        self.prompts = []
    def __call__(self, prompt):
        self.prompts.append(prompt)
        return "mocked provider response"


class StrandsProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repository = night_shift_repository()
        workflow = ClearanceCaseWorkflow(self.repository, NIGHT_SHIFT_INTENT, LocalProjectStore(Path(self.temp.name) / "state.json"))
        self.service = ClearanceApplicationService(workflow, LocalInbox())
        self.agent = FakeAgent()
        self.provider = StrandsProvider(
            self.repository, self.service, StrandsConfig("us-east-1", "test.model", "profile"),
            agent_factory=lambda config, prompt, tools: self.agent,
            tool_factory=lambda service: ["mock-tool"],
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_action_request_becomes_strands_prompt_without_sdk(self):
        result = self.provider.execute(AgentActionRequest("action-1", "REQUEST_EVIDENCE", "daniel", "No evidence record was found."))
        self.assertTrue(result.accepted)
        self.assertIn("REQUEST_EVIDENCE", self.agent.prompts[0])
        self.assertIn("daniel", self.agent.prompts[0])

    def test_run_uses_mocked_agent_and_preserves_deterministic_results(self):
        results = self.provider.run(NIGHT_SHIFT_INTENT)
        self.assertEqual(next(result for result in results if result.item.id == "archive").status, "SCOPE_MISMATCH")
        self.assertEqual(len(self.agent.prompts), 1)

    def test_system_prompt_enforces_legal_escalation(self):
        self.assertIn("no legal advice", SYSTEM_PROMPT.lower())
        self.assertIn("fair-use", SYSTEM_PROMPT.lower())
        self.assertIn("human review", SYSTEM_PROMPT.lower())

    def test_config_requires_model_id(self):
        with self.assertRaises(ValueError):
            StrandsConfig("us-east-1", "").validate()

    def test_package_and_smoke_test_modules_import(self):
        package = importlib.import_module("adapters.strands")
        smoke_test = importlib.import_module("adapters.strands.smoke_test")
        self.assertIs(package.StrandsProvider, StrandsProvider)
        self.assertTrue(smoke_test.__doc__)

    def test_provider_failure_does_not_mutate_before_request(self):
        failed = StrandsProvider(self.repository, self.service, StrandsConfig("us-east-1", "test.model"), agent_factory=lambda *args: lambda prompt: (_ for _ in ()).throw(RuntimeError("throttling")), tool_factory=lambda service: [])
        failed.service = ClearanceApplicationService(self.service.workflow, failed)
        with self.assertRaises(ProviderExecutionError):
            failed.service.request_evidence("daniel")
        self.assertEqual(failed.service.workflow.state.events, [])

    def test_requests_mutate_once_for_local_and_strands_tool_dispatch(self):
        for method, item_id, event_type in (
            ("request_evidence", "daniel", EventType.EVIDENCE_REQUESTED),
            ("request_human_review", "painting", EventType.HUMAN_REVIEW_REQUESTED),
        ):
            for tool_calls in (0, 1, 2):
                with self.subTest(method=method, tool_calls=tool_calls):
                    store = LocalProjectStore(Path(self.temp.name) / f"{method}-{tool_calls}.json")
                    workflow = ClearanceCaseWorkflow(night_shift_repository(), NIGHT_SHIFT_INTENT, store)
                    service = ClearanceApplicationService(workflow, LocalInbox())
                    if tool_calls:
                        # Use the real tool bodies; only SDK decoration and inference are replaced.
                        with patch.dict("sys.modules", {"strands": SimpleNamespace(tool=lambda function: function)}):
                            tools = {tool.__name__: tool for tool in build_strands_tools(service)}
                        def agent(prompt):
                            for _ in range(tool_calls):
                                tools[method](item_id)
                            return "Tool completed"
                        service.actions = StrandsProvider(workflow.repository, service, StrandsConfig("us-east-1", "test.model"), agent_factory=lambda *args: agent, tool_factory=lambda service: list(tools.values()))
                    else:
                        service.actions = DeterministicProvider(workflow.repository, service)
                    case = getattr(service, method)(item_id)
                    self.assertEqual(len(service.action_results), 1)
                    self.assertEqual([e.event_type for e in workflow.state.events], [EventType.PROJECT_SCAN_STARTED, EventType.CLEARANCE_ITEM_IDENTIFIED, event_type])
                    self.assertEqual(len(store.load().events), 3)
                    if method == "request_evidence":
                        self.assertEqual(case.requests, ["request-daniel-1"])
                    self.assertTrue(case.paused)

    def test_failed_dispatch_can_be_retried_without_stale_request(self):
        attempts = 0
        def agent(prompt):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("throttling")
            self.service.request_evidence("daniel", dispatch=False)
            return "Tool completed"
        self.provider.agent_factory = lambda *args: agent
        self.service.actions = self.provider
        with self.assertRaises(ProviderExecutionError):
            self.service.request_evidence("daniel")
        self.assertEqual(self.service.workflow.state.events, [])
        case = self.service.request_evidence("daniel")
        self.assertEqual(case.requests, ["request-daniel-1"])
        self.assertEqual(sum(e.event_type == EventType.EVIDENCE_REQUESTED for e in self.service.workflow.state.events), 1)


if __name__ == "__main__":
    unittest.main()
