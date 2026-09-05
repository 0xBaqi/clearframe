"""Compatibility exports; local JSON persistence is an adapter."""
from adapters.local.store import LocalProjectStore
from packages.core.state.models import CaseState, ProjectState

__all__ = ["CaseState", "ProjectState", "LocalProjectStore"]
