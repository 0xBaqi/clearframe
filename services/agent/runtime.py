"""Provider-neutral application composition."""
from dataclasses import dataclass, field

from packages.agent_contract import AgentActionExecutor, AgentActionRequest, AgentActionResult, AgentProvider
from packages.core.clearance import ClearanceCaseWorkflow
from packages.core.types import ClearanceResult, EvidenceRecord, ProjectIntent


def run_clearance(provider: AgentProvider, intent: ProjectIntent) -> list[ClearanceResult]:
    return provider.run(intent)


@dataclass
class ClearanceApplicationService:
    workflow: ClearanceCaseWorkflow
    actions: AgentActionExecutor
    action_results: list[AgentActionResult] = field(default_factory=list)

    def _dispatch(self, action: str, request_id: str, item_id: str, reason: str, evidence_id: str | None = None) -> AgentActionResult:
        result = self.actions.execute(AgentActionRequest(request_id, action, item_id, reason, evidence_id))
        self.action_results.append(result)
        return result

    def request_evidence(self, item_id: str):
        case = self.workflow.create_document_request(item_id)
        self._dispatch("REQUEST_EVIDENCE", case.requests[-1], item_id, "No evidence record was found.")
        return case

    def receive_document(self, record: EvidenceRecord):
        request_count = len(self.workflow.state.cases.get(record.item_id).requests) if record.item_id in self.workflow.state.cases else 0
        case = self.workflow.receive_evidence(record)
        if len(case.requests) > request_count and case.requests[-1].startswith("correction-"):
            self._dispatch("REQUEST_CORRECTION", case.requests[-1], record.item_id, "Signature or date is missing.", record.id)
        return case

    def request_human_review(self, item_id: str):
        case = self.workflow.begin_human_review(item_id)
        self._dispatch("REQUEST_HUMAN_REVIEW", f"review-{item_id}-{len(case.evidence_ids) + 1}", item_id, "Evidence cannot establish administrative permission scope.")
        return case

    def record_human_decision(self, item_id: str, decision: str):
        return self.workflow.record_human_decision(item_id, decision)
