from backend.evidence_tools import SeedEvidenceRepository
from backend.models import ClearanceItem, EvidenceRecord, ProjectIntent


NIGHT_SHIFT_INTENT = ProjectIntent(
    distribution=["YouTube", "Streaming platforms", "Film festivals"],
    territories=["Worldwide"],
    end_date="2028-01-01",
)


def night_shift_repository() -> SeedEvidenceRepository:
    items = [
        ClearanceItem("sarah", "Sarah Cole", "performer/appearance", "Scene 01"),
        ClearanceItem("daniel", "Daniel Reed", "performer/appearance", "Scene 02"),
        ClearanceItem("archive", "News Clip #03", "archive footage", "Scene 12"),
        ClearanceItem("painting", "Painting in Scene 7", "artwork/image", "Scene 07"),
    ]
    evidence = [
        EvidenceRecord("sarah-release", "sarah", "appearance release", True, True, ["YouTube", "Streaming platforms", "Film festivals"], ["Worldwide"], "2030-01-01", "high", "Signed performer release."),
        EvidenceRecord("archive-license", "archive", "archive footage licence", True, True, ["Film festivals"], ["US", "Canada"], "2026-12-31", "high", "Festival-only archive licence."),
        EvidenceRecord("painting-photo", "painting", "production still", None, None, None, None, None, "low", "Artwork visible; rights holder and permission cannot be established from still."),
    ]
    return SeedEvidenceRepository(items, evidence)
