"""Provider-neutral application service used by future API/runtime entry points."""
from packages.agent_contract import AgentProvider
from packages.core.types import ClearanceResult, ProjectIntent


def run_clearance(provider: AgentProvider, intent: ProjectIntent) -> list[ClearanceResult]:
    return provider.run(intent)
