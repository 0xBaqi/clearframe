"use client";

import { useState } from "react";

type Ticket = { scene: string; name: string; category: string; status: "EVIDENCE_COMPLETE" | "EVIDENCE_MISSING" | "SCOPE_MISMATCH" | "HUMAN_REVIEW"; note: string; chain: string[]; tape: string[] };

const tickets: Ticket[] = [
  { scene: "01", name: "Sarah Cole", category: "Appearance release", status: "EVIDENCE_COMPLETE", note: "Signed release supports declared project intent.", chain: ["Sarah Cole", "Appearance release · signed", "Worldwide · YouTube / streaming / festivals", "Intent comparison"], tape: ["Found Sarah release", "Read signature and date", "Compared declared scope", "Evidence complete"] },
  { scene: "02", name: "Daniel Reed", category: "Appearance release", status: "EVIDENCE_MISSING", note: "No submitted evidence record was found.", chain: ["Daniel Reed", "No linked evidence", "Document request needed"], tape: ["Searched evidence index", "No release found", "Marked evidence missing"] },
  { scene: "12", name: "News Clip #03", category: "Archive footage", status: "SCOPE_MISMATCH", note: "Evidence supports festivals in the US and Canada only; declared intent is worldwide and includes YouTube and streaming.", chain: ["News Clip #03", "Archive licence", "US + Canada · Film festivals", "Intent comparison"], tape: ["Found archive licence", "Read scope fields", "Compared declared scope", "Scope mismatch"] },
  { scene: "07", name: "Painting in Scene 7", category: "Artwork / image", status: "HUMAN_REVIEW", note: "The production still cannot establish a rights holder or usable permission scope.", chain: ["Painting in Scene 7", "Production still", "No permission fields", "Human review route"], tape: ["Found production still", "Permission scope unavailable", "Escalated for human review"] }
];

const label: Record<Ticket["status"], string> = { EVIDENCE_COMPLETE: "Evidenced", EVIDENCE_MISSING: "Missing", SCOPE_MISMATCH: "Scope mismatch", HUMAN_REVIEW: "Human review" };

export default function Home() {
  const [selected, setSelected] = useState(tickets[0]);
  return <main>
    <header><span className="brand">CLEARFRAME</span><span className="project">NIGHT SHIFT <i>short film · fictional demo</i></span><span className="meter">1 / 4 EVIDENCED</span></header>
    <section className="brief"><p>INTENDED USE</p><strong>YouTube · Streaming platforms · Film festivals</strong><span>Worldwide</span></section>
    <section className="reel-wrap" aria-label="Clearance Reel"><div className="section-label">CLEARANCE REEL <span>SELECT A TICKET TO TRACE ITS EVIDENCE</span></div><div className="reel-line" />
      <div className="reel">{tickets.map((ticket) => <button onClick={() => setSelected(ticket)} className={`ticket ${ticket.status} ${selected.name === ticket.name ? "selected" : ""}`} key={ticket.name}><small>SCENE {ticket.scene}</small><b>{ticket.name}</b><em>{ticket.category}</em><mark>{label[ticket.status]}</mark></button>)}</div>
    </section>
    <section className="desk"><article className="evidence"><div className="section-label">EVIDENCE CHAIN <span>ADMINISTRATIVE RECORD, NOT LEGAL ADVICE</span></div><h1>{selected.name}</h1><div className={`status ${selected.status}`}>{label[selected.status]}</div><p className="note">{selected.note}</p><ol>{selected.chain.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, "0")}</span>{step}</li>)}</ol></article>
      <aside className="tape"><div className="section-label">OPERATIONS TAPE</div><p className="operator">CLEARFRAME / LOCAL AGENT</p>{selected.tape.map((event, index) => <div className="event" key={event}><time>0{index + 1}:2{index}</time>{event}</div>)}<footer>STATUS IS AN EVIDENCE WORKFLOW RESULT. HUMAN REVIEW MAY BE REQUIRED.</footer></aside>
    </section>
  </main>;
}
