from __future__ import annotations

from typing import Protocol

from backend.evidence_tools import ClearanceTools, SeedEvidenceRepository
from backend.models import ClearanceResult, EvidenceRecord, ProjectIntent, Status


class ClearanceAgent(Protocol):
    def run(self, intent: ProjectIntent) -> list[ClearanceResult]: ...


class StrandsClearanceAgent:
    """Offline Strands orchestration adapter.

    Milestone 1 intentionally uses deterministic tool orchestration so fixture tests
    are repeatable without AWS credentials. Its tool boundary is the same boundary
    a Strands Agent + Bedrock model will call in the hosted implementation.
    """

    def __init__(self, repository: SeedEvidenceRepository):
        self.tools = ClearanceTools(repository)

    def run(self, intent: ProjectIntent) -> list[ClearanceResult]:
        results: list[ClearanceResult] = []
        for item in self.tools.list_clearance_items():
            start = len(self.tools.operations)
            evidence = self.tools.find_evidence(item)
            if not evidence:
                results.append(ClearanceResult(item, Status.EVIDENCE_MISSING, "No submitted evidence record was found.", [item.name], self.tools.operations[start:]))
                continue

            record = self.tools.read_permission_scope(evidence[0])
            chain = [item.name, f"{record.document_type} ({record.id})"]
            if record.signed is not True or record.dated is not True:
                reason = "The submitted record is incomplete: signature and date are required administrative fields."
                self.tools.escalate_for_human_review(item, reason)
                results.append(ClearanceResult(item, Status.HUMAN_REVIEW, reason, chain, self.tools.operations[start:]))
                continue

            comparison = self.tools.compare_scope_to_intent(record, intent)
            chain.append("Project intent comparison")
            if not comparison.matches:
                results.append(ClearanceResult(item, Status.SCOPE_MISMATCH, " ".join(comparison.reasons), chain, self.tools.operations[start:]))
            else:
                results.append(ClearanceResult(item, Status.EVIDENCE_COMPLETE, "Submitted evidence has complete administrative fields and supports the declared intent.", chain, self.tools.operations[start:]))
        return results
