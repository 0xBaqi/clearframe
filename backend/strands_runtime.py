"""Compatibility factory for the dedicated Strands adapter."""
from adapters.strands import StrandsAgentProvider


def build_agent(repository):
    return StrandsAgentProvider(repository)
