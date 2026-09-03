"""Hosted Strands entry point for the same product-level agent contract.

This module deliberately stays separate from the offline fixture so the hackathon
demo works without AWS credentials. Configure AWS/Bedrock, then install
`backend/requirements.txt` to use the Strands runtime in the next milestone.
"""

from backend.agent import StrandsClearanceAgent
from backend.evidence_tools import SeedEvidenceRepository


def build_agent(repository: SeedEvidenceRepository) -> StrandsClearanceAgent:
    """Return the product adapter consumed by the API layer.

    The adapter is named for its Strands implementation target. A future hosted
    version supplies Strands `Agent` and Bedrock model configuration here while
    preserving this public construction point and the evidence-tool contract.
    """
    return StrandsClearanceAgent(repository)
