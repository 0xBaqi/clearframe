"""Controlled local inbox adapter used for offline action delivery."""
from dataclasses import dataclass, field

from packages.agent_contract import AgentActionRequest, AgentActionResult


@dataclass
class LocalInbox:
    deliveries: list[AgentActionRequest] = field(default_factory=list)

    def execute(self, request: AgentActionRequest) -> AgentActionResult:
        self.deliveries.append(request)
        return AgentActionResult(request.id, True, f"local-inbox-{len(self.deliveries)}", "Delivered to the controlled local inbox.")
