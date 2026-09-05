"""Compatibility exports; local evidence is an adapter, evaluation is core."""
from adapters.local.repository import LocalEvidenceRepository
from packages.core.clearance.engine import EvidenceTools as ClearanceTools
from packages.core.evidence.evaluation import ScopeComparison


class SeedEvidenceRepository(LocalEvidenceRepository):
    """Deprecated local-demo name retained for existing callers."""
