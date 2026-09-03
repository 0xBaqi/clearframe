# ClearFrame design direction

ClearFrame should feel like a working production-clearance desk: tactile, linear, and evidence-first. It must not resemble a generic SaaS dashboard or lead with a chatbot.

## Primary surfaces

### Clearance Reel

The centre of the product is a horizontal, scene-aware reel. Each clearance item is a physical-looking ticket on the reel, marked by an operational state rather than a KPI card. Selecting a ticket reveals its records and actions.

### Evidence Chain

The detail view stacks source records in the order the agent used them: item → submitted record → extracted permission → project-intent comparison → conclusion. A person can always see why a status was produced.

### Operations Tape

A narrow running tape records every operational step: record found, field read, scope compared, escalation created. This is an activity trace, not an opaque reasoning transcript.

## Visual language

- Ink, paper, tape, filing-label, and production-call-sheet cues—not cards, gradients, or generic analytics.
- Dark charcoal workspace with warm paper tickets; status colour is restrained and always paired with words/icons.
- Condensed display typography for labels and scenes; a readable mono/utility face for evidence metadata.
- The agent is present as an operator in the tape, never as a full-screen conversational interface.

## Status vocabulary

`EVIDENCE_COMPLETE`, `EVIDENCE_MISSING`, `SCOPE_MISMATCH`, `HUMAN_REVIEW`, and later `AWAITING_RESPONSE` are operational labels. They must be accompanied by plain-language context and never imply legal clearance.
