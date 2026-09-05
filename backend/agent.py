"""Compatibility entry point for the Strands adapter."""
from adapters.strands import StrandsAgentProvider
from packages.agent_contract import AgentProvider as ClearanceAgent


class StrandsClearanceAgent(StrandsAgentProvider):
    pass
