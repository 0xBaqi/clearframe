"""Provider-neutral application composition."""
from dataclasses import dataclass, field
from typing import Callable

from packages.agent_contract import AgentActionExecutor, AgentActionRequest, AgentActionResult, AgentProvider
from packages.core.clearance import ClearanceCaseWorkflow
from packages.core.state import CaseState
from packages.core.types import ClearanceResult, EvidenceRecord, ProjectIntent


def run_clearance(provider: AgentProvider, intent: ProjectIntent) -> list[ClearanceResult]:
    return provider.run(intent)


@dataclass
class ClearanceApplicationService:
    workflow: ClearanceCaseWorkflow
    actions: AgentActionExecutor
    action_results: list[AgentActionResult] = field(default_factory=list)
    _request_cases: dict[tuple[str, str], CaseState | None] = field(default_factory=dict, init=False, repr=False)

    def _dispatch(self, action: str, request_id: str, item_id: str, reason: str, evidence_id: str | None = None) -> AgentActionResult:
        result = self.actions.execute(AgentActionRequest(request_id, action, item_id, reason, evidence_id))
        self.action_results.append(result)
        return result

    def _request(self, action: str, request_id: str, item_id: str, reason: str, mutation: Callable[[str], CaseState], dispatch: bool) -> CaseState:
        key = (action, item_id)
        if dispatch and key not in self._request_cases:
            # A Strands tool and its caller share one mutation within this dispatch.
            self._request_cases[key] = None
            try:
                self._dispatch(action, request_id, item_id, reason)
                return self._request(action, request_id, item_id, reason, mutation, False)
            finally:
                del self._request_cases[key]
        case = self._request_cases.get(key)
        if case is None:
            case = mutation(item_id)
            if key in self._request_cases:
                self._request_cases[key] = case
        return case

    def request_evidence(self, item_id: str, dispatch: bool = True):
        return self._request("REQUEST_EVIDENCE", f"request-{item_id}", item_id, "No evidence record was found.", self.workflow.create_document_request, dispatch)

    def receive_document(self, record: EvidenceRecord):
        request_count = len(self.workflow.state.cases.get(record.item_id).requests) if record.item_id in self.workflow.state.cases else 0
        case = self.workflow.receive_evidence(record)
        if len(case.requests) > request_count and case.requests[-1].startswith("correction-"):
            self._dispatch("REQUEST_CORRECTION", case.requests[-1], record.item_id, "Signature or date is missing.", record.id)
        return case

    def request_human_review(self, item_id: str, dispatch: bool = True):
        return self._request("REQUEST_HUMAN_REVIEW", f"review-{item_id}", item_id, "Evidence cannot establish administrative permission scope.", self.workflow.begin_human_review, dispatch)

    def record_human_decision(self, item_id: str, decision: str):
        return self.workflow.record_human_decision(item_id, decision)
