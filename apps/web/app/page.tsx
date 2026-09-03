"use client";

import { useState } from "react";

type EventType = "PROJECT_SCAN_STARTED" | "CLEARANCE_ITEM_IDENTIFIED" | "EVIDENCE_MATCHED" | "EVIDENCE_REQUESTED" | "DOCUMENT_RECEIVED" | "DOCUMENT_DEFICIENCY_FOUND" | "CORRECTION_REQUESTED" | "SCOPE_MISMATCH_DETECTED" | "HUMAN_REVIEW_REQUESTED" | "HUMAN_DECISION_RECORDED" | "CASE_RESUMED" | "ITEM_EVIDENCE_COMPLETE";
type Ticket = { scene: string; name: string; category: string; status: "EVIDENCE_COMPLETE" | "EVIDENCE_MISSING" | "SCOPE_MISMATCH" | "HUMAN_REVIEW"; note: string; chain: string[]; events: EventType[] };

const tickets: Ticket[] = [
  { scene: "01", name: "Sarah Cole", category: "Appearance release", status: "EVIDENCE_COMPLETE", note: "Signed release supports declared project intent.", chain: ["Sarah Cole", "Appearance release · signed", "Worldwide · YouTube / streaming / festivals", "Intent comparison"], events: ["EVIDENCE_MATCHED", "ITEM_EVIDENCE_COMPLETE"] },
  { scene: "02", name: "Daniel Reed", category: "Appearance release", status: "EVIDENCE_MISSING", note: "No submitted evidence record was found.", chain: ["Daniel Reed", "No linked evidence", "Document request needed"], events: ["PROJECT_SCAN_STARTED", "CLEARANCE_ITEM_IDENTIFIED", "EVIDENCE_REQUESTED"] },
  { scene: "12", name: "News Clip #03", category: "Archive footage", status: "SCOPE_MISMATCH", note: "Evidence supports festivals in the US and Canada only; declared intent is worldwide and includes YouTube and streaming.", chain: ["News Clip #03", "Archive licence", "US + Canada · Film festivals", "Intent comparison"], events: ["EVIDENCE_MATCHED", "SCOPE_MISMATCH_DETECTED"] },
  { scene: "07", name: "Painting in Scene 7", category: "Artwork / image", status: "HUMAN_REVIEW", note: "The production still cannot establish a rights holder or usable permission scope.", chain: ["Painting in Scene 7", "Production still", "No permission fields", "Human review route"], events: ["HUMAN_REVIEW_REQUESTED"] }
];
const label: Record<Ticket["status"], string> = { EVIDENCE_COMPLETE: "Evidenced", EVIDENCE_MISSING: "Missing", SCOPE_MISMATCH: "Scope mismatch", HUMAN_REVIEW: "Human review" };
const eventLabel = (event: EventType) => event.replaceAll("_", " ");

export default function Home() {
  const [selected, setSelected] = useState(tickets[0]);
  return <main><header><span className="brand">CLEARFRAME</span><span className="project">NIGHT SHIFT <i>short film · fictional demo</i></span><span className="meter">1 / 4 EVIDENCED</span></header><section className="brief"><p>INTENDED USE</p><strong>YouTube · Streaming platforms · Film festivals</strong><span>Worldwide</span></section><section className="reel-wrap" aria-label="Clearance Reel"><div className="section-label">CLEARANCE REEL <span>SELECT A TICKET TO TRACE ITS EVIDENCE</span></div><div className="reel-line" /><div className="reel">{tickets.map((ticket) => <button onClick={() => setSelected(ticket)} className={`ticket ${ticket.status} ${selected.name === ticket.name ? "selected" : ""}`} key={ticket.name}><small>SCENE {ticket.scene}</small><b>{ticket.name}</b><em>{ticket.category}</em><mark>{label[ticket.status]}</mark></button>)}</div></section><section className="desk"><article className="evidence"><div className="section-label">EVIDENCE CHAIN <span>ADMINISTRATIVE RECORD, NOT LEGAL ADVICE</span></div><h1>{selected.name}</h1><div className={`status ${selected.status}`}>{label[selected.status]}</div><p className="note">{selected.note}</p><ol>{selected.chain.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, "0")}</span>{step}</li>)}</ol></article><aside className="tape"><div className="section-label">OPERATIONS TAPE</div><p className="operator">CLEARFRAME / LOCAL AGENT</p>{selected.events.map((event, index) => <div className="event" key={event}><time>0{index + 1}:2{index}</time>{eventLabel(event)}</div>)}<footer>STATUS IS AN EVIDENCE WORKFLOW RESULT. HUMAN REVIEW MAY BE REQUIRED.</footer></aside></section></main>;
}
