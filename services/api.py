"""Thin local HTTP API for the provider-neutral ClearFrame application service."""
from __future__ import annotations
import json, os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from adapters.local import DeterministicProvider, LocalProjectStore
from adapters.strands import StrandsProvider
from backend.seed import NIGHT_SHIFT_INTENT, night_shift_repository
from demo.night_shift.run_agent_demo import daniel_release
from packages.core.clearance import ClearanceCaseWorkflow
from packages.core.types import EvidenceRecord
from services.agent import ClearanceApplicationService

class NightShiftAPI:
    def __init__(self, state_path: Path | None = None):
        self.state_path = state_path or Path(os.getenv("CLEARFRAME_STATE_PATH", ".clearframe/night-shift.json"))
    def service(self):
        repository = night_shift_repository(); workflow = ClearanceCaseWorkflow(repository, NIGHT_SHIFT_INTENT, LocalProjectStore(self.state_path))
        provider_name = os.getenv("CLEARFRAME_AGENT_PROVIDER", "local").lower()
        if provider_name == "strands":
            provider = StrandsProvider(repository, None)
        elif provider_name == "local":
            provider = DeterministicProvider(repository)
        else: raise ValueError("CLEARFRAME_AGENT_PROVIDER must be local or strands.")
        service = ClearanceApplicationService(workflow, provider); provider.service = service
        return service, provider
    def payload(self):
        service, _ = self.service(); state = service.workflow.state
        return {"project_id": state.project_id, "items": [asdict(item) for item in service.workflow.repository.list_clearance_items()], "intent": asdict(NIGHT_SHIFT_INTENT), "cases": {key: {**asdict(case), "status": case.status.value} for key, case in state.cases.items()}, "events": [{**asdict(event), "event_type": event.event_type.value, "actor": event.actor.value} for event in state.events]}
    def advance(self):
        service, provider = self.service(); state = service.workflow.state; types = [event.event_type.value for event in state.events]
        if not types: service.receive_document(service.workflow.repository.find_evidence("sarah")[0])
        elif "SCOPE_MISMATCH_DETECTED" not in types: service.receive_document(service.workflow.repository.find_evidence("archive")[0])
        elif "EVIDENCE_REQUESTED" not in types: service.request_evidence("daniel")
        elif "HUMAN_REVIEW_REQUESTED" not in types: service.request_human_review("painting")
        elif "daniel-unsigned" not in [event.evidence_id for event in state.events]: service.receive_document(daniel_release("daniel-unsigned", False))
        elif "daniel-signed" not in [event.evidence_id for event in state.events]: service.receive_document(daniel_release("daniel-signed", True))
        return self.payload()
    def complete(self):
        while "daniel-signed" not in [event.get("evidence_id") for event in self.payload()["events"]]: self.advance()
        service, _ = self.service()
        if not any(event.event_type.value == "HUMAN_DECISION_RECORDED" for event in service.workflow.state.events): service.record_human_decision("painting", "Artwork will be removed from the final cut.")
        return self.payload()
    def receive(self, data):
        record = EvidenceRecord(**data); service, _ = self.service(); service.receive_document(record); return self.payload()
    def decision(self, data):
        decision = data.get("decision", "")
        if not isinstance(decision, str) or not decision.strip(): raise ValueError("A human decision is required.")
        service, _ = self.service(); service.record_human_decision("painting", decision); return self.payload()
    def reset(self):
        if self.state_path.exists(): self.state_path.unlink()
        return self.payload()

def handler_for(api):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, body):
            encoded=json.dumps(body).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin",os.getenv("CLEARFRAME_CORS_ORIGIN","http://localhost:3000")); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers(); self.wfile.write(encoded)
        def do_OPTIONS(self): self.send_json(204,{})
        def do_GET(self):
            try:
                path = urlparse(self.path).path
                if path == "/api/project": self.send_json(200,api.payload())
                elif path == "/api/events": self.send_json(200,{"events": api.payload()["events"]})
                else: self.send_json(404,{"error":"Not found"})
            except Exception as error: self.send_json(500,{"error":str(error)})
        def do_POST(self):
            try:
                length=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(length) or b"{}")
                path=urlparse(self.path).path
                if path=="/api/demo/advance": body=api.advance()
                elif path=="/api/demo/complete": body=api.complete()
                elif path=="/api/demo/reset": body=api.reset()
                elif path=="/api/documents": body=api.receive(data)
                elif path=="/api/human-decision": body=api.decision(data)
                else: self.send_json(404,{"error":"Not found"}); return
                self.send_json(200,body)
            except (ValueError, TypeError) as error: self.send_json(400,{"error":str(error)})
            except Exception as error: self.send_json(500,{"error":str(error)})
        def log_message(self,*args): pass
    return Handler

def main():
    api=NightShiftAPI(); server=ThreadingHTTPServer((os.getenv("CLEARFRAME_API_HOST","127.0.0.1"),int(os.getenv("CLEARFRAME_API_PORT","8000"))),handler_for(api)); print("ClearFrame API listening on http://127.0.0.1:8000"); server.serve_forever()
if __name__=="__main__": main()
