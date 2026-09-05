from dataclasses import dataclass

from packages.core.types import EvidenceRecord, ProjectIntent


@dataclass(frozen=True)
class ScopeComparison:
    matches: bool
    reasons: list[str]


def compare_scope_to_intent(record: EvidenceRecord, intent: ProjectIntent) -> ScopeComparison:
    """Administrative comparison of declared fields; never a legal conclusion."""
    reasons: list[str] = []
    if record.distribution is None or record.territories is None:
        reasons.append("The record does not provide a usable permission scope.")
    else:
        missing_distribution = sorted(set(intent.distribution) - set(record.distribution))
        if missing_distribution:
            reasons.append("Distribution excludes: " + ", ".join(missing_distribution) + ".")
        if "Worldwide" in intent.territories and "Worldwide" not in record.territories:
            reasons.append("Territory is limited to: " + ", ".join(record.territories) + ".")
    if intent.end_date and record.expires_on and record.expires_on < intent.end_date:
        reasons.append(f"Permission expires on {record.expires_on} before the project end date.")
    return ScopeComparison(matches=not reasons, reasons=reasons)
