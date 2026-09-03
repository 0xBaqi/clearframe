"""Complete offline deterministic NIGHT SHIFT demonstration."""
from __future__ import annotations
import os, tempfile
from pathlib import Path
from adapters.local import DeterministicProvider, LocalProjectStore
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from packages.core.clearance import ClearanceCaseWorkflow
from packages.core.types import EvidenceRecord
from services.agent import ClearanceApplicationService

def daniel_release(record_id, signed):
    return EvidenceRecord(record_id, "daniel", "appearance release", signed, True, list(NIGHT_SHIFT_INTENT.distribution), ["Worldwide"], "2030-01-01", "high", "Demo release.")

def build(state_path: Path):
    repo = night_shift_repository(); workflow = ClearanceCaseWorkflow(repo, NIGHT_SHIFT_INTENT, LocalProjectStore(state_path)); provider = DeterministicProvider(repo); service = ClearanceApplicationService(workflow, provider); provider.service = service; return provider, service

def run_demo(state_path: Path | None = None):
    temporary = None
    if state_path is None:
        temporary = tempfile.TemporaryDirectory(); state_path = Path(temporary.name) / "night-shift.json"
    provider, service = build(state_path)
    if not service.workflow.state.events: provider.start_night_shift()
    service.receive_document(daniel_release("daniel-unsigned", False))
    # Rebuild from persisted state to prove that waiting work resumes rather than restarts.
    provider, service = build(state_path)
    service.receive_document(daniel_release("daniel-signed", True))
    service.record_human_decision("painting", "Artwork will be removed from the final cut.")
    return service.workflow.state

def main():
    state = run_demo(Path(os.environ["CLEARFRAME_DEMO_STATE"]) if os.getenv("CLEARFRAME_DEMO_STATE") else None)
    print("CLEARFRAME / NIGHT SHIFT")
    for event in state.events: print(f"{event.sequence:02d} {event.actor} {event.event_type} {event.item_id} — {event.detail}")
    for item_id, case in state.cases.items(): print(f"FINAL {item_id}: {case.status}")
if __name__ == "__main__": main()
