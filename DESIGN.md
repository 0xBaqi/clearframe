# ClearFrame visual system

## Product identity and primary user
ClearFrame is a rights-and-release clearance workspace for small creative production teams. Producers and clearance coordinators need to identify incomplete records, inspect supporting evidence, and understand where human review is required. Operational completeness is not a legal clearance guarantee.

## Design metaphor
Production clearance room, evidence dossier, and rights ledger. A flat subject board leads into a selected evidence dossier, with the recorded production audit below it. No simulated paperwork, decorative footage, or theatrical command-centre styling.

## Information hierarchy
Status → subject → evidence → explanation → metadata. The project header shows the real completed count over the actual subject count. Each board row presents subject, type, existing status, and latest recorded explanation. Problem statuses receive restrained emphasis; completed explanations are quieter. Subject order remains stable during demo advancement and keyboard navigation.

## Typography
Use a readable system sans-serif with no remote font dependency. Project title: 28px; dossier title: 24px; subjects: 15–16px; evidence values: 14px. Small uppercase labels structure sections. Technical identifiers and timestamps remain secondary. Counts use tabular numerals. Never use oversized marketing typography.

## Spacing
Use a 4px base rhythm. Desktop page gutters are 40px, reducing to 24px and 16px. Rows use 18px vertical padding; dossiers use 24px inset. Whitespace and separators distinguish sections instead of nested containers.

## Status semantics
Preserve the existing event-derived status rules and vocabulary verbatim. CLEARED uses dark green and means evidence supports the configured declared use. SCOPE CONFLICT, EVIDENCE NEEDED, and DOCUMENT DEFICIENCY use rust. HUMAN HOLD and HUMAN REVIEW use slate, indicating a deliberate human boundary rather than failure. IN REVIEW uses ink. Every status is readable text; color is supplemental. Never substitute invented counts or static fixture outcomes for the evolving recorded workflow.

## Borders, radius, elevation, and cards
Use one-pixel section/row separators and a stronger project rule. Buttons may have a 3px radius. The selected dossier has a white surface; the selected subject has an ink left edge. Human review has a light slate inset. No shadows. Do not wrap individual evidence facts or each board row in a card.

## Evidence and activity
Show existing document details, references, comparison reasons, and recorded decisions. Latest event details support board reasons. The production audit is a native expandable section in document flow, displaying real events and their details. Keep its timestamps and actor metadata subordinate. Do not manufacture permitted-scope fields, recommendations, activity, or reasoning.

## Responsive and accessibility behavior
At 1000px, reduce board columns and stack the evidence chain. At 600px, each row stacks subject, status, and reason; controls wrap and dossier headers stack. Long evidence text wraps. Audit entries stack their content below metadata. Use native buttons and details/summary, readable status text, visible blue focus outlines, and aria-pressed for subject selection. No fixed overlay should obscure the demo. Rendered mobile and keyboard verification is required before submission; source inspection alone is insufficient.

## Anti-patterns
- Generic SaaS dashboard
- Excessive cards or rounded containers
- Gradient text, decorative gradients, or glassmorphism
- Meaningless icon tiles
- Unnecessary shadows
- Giant KPI cards
- Equal visual weight everywhere
- Generic AI copy
- Chatbot UI
- Fake agent activity

## Preservation boundary
This refinement changes presentation only. Keep engine rules, provider architecture, local/Strands/Bedrock integrations, API contracts, fixtures, tests, routing, configuration, and demo event transitions unchanged.
