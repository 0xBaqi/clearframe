"""Offline provider that drives the same application-service action contracts as Strands."""
from packages.agent_contract import AgentActionRequest, AgentActionResult, AgentProvider
from packages.core.clearance import ClearanceEngine

class DeterministicProvider(AgentProvider):
    def __init__(self, repository, service=None): self.repository, self.service, self.actions = repository, service, []
    def execute(self, request: AgentActionRequest) -> AgentActionResult:
        self.actions.append(request)
        return AgentActionResult(request.id, True, f"deterministic-{len(self.actions)}", "Recorded for deterministic execution.")
    def run(self, intent):
        return ClearanceEngine(self.repository).run(intent)
    def start_night_shift(self):
        # Existing records are processed through the same application service as external arrivals.
        for item_id in ("sarah", "archive"):
            record = self.repository.find_evidence(item_id)[0]
            self.service.receive_document(record)
        self.service.request_evidence("daniel")
        self.service.request_human_review("painting")
