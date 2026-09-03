"""Strands integration seam.

The local deterministic provider delegates to the core engine until a configured
Strands/Bedrock runtime is supplied. No Strands or AWS concepts enter core.
"""
from packages.agent_contract import AgentProvider
from packages.core.clearance import ClearanceEngine
from packages.core.evidence import EvidenceRepository
from packages.core.types import ClearanceResult, ProjectIntent


class StrandsAgentProvider(AgentProvider):
    def __init__(self, repository: EvidenceRepository):
        self.engine = ClearanceEngine(repository)

    def run(self, intent: ProjectIntent) -> list[ClearanceResult]:
        return self.engine.run(intent)
