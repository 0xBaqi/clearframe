from typing import Protocol

from packages.core.types import ClearanceResult, ProjectIntent


class AgentProvider(Protocol):
    """Provider contract. Product callers never import a model SDK."""

    def run(self, intent: ProjectIntent) -> list[ClearanceResult]: ...
