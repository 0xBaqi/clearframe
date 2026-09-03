# ClearFrame architecture

## Boundary

The frontend is a Next.js + TypeScript application. The agent service is Python. The frontend consumes a small product-facing API contract; it never depends directly on a particular model or agent framework.

```
Next.js Clearance Reel
        │
        ▼
ClearFrame API contract
        │
        ▼
Agent adapter ──► evidence tools ──► record/file adapters
        │                                │
        │                                ├─ local seed (Milestone 1)
        │                                ├─ S3 (later)
        │                                └─ DynamoDB (later state)
        ▼
Strands implementation ──► Amazon Bedrock / AgentCore Runtime (later deployment)
```

## Adapter rule

`ClearanceAgent` is the core interface. It accepts a project intent and evidence repository and returns `ClearanceRun`. `StrandsClearanceAgent` is the Milestone 1 implementation. A Gemini, Nebius, or another agent-framework implementation can satisfy the same interface without changing statuses, tools, frontend contracts, or persistence models.

## Agent design

The tool layer owns facts:

- `list_clearance_items` identifies the records to review.
- `find_evidence` returns submitted records for an item.
- `read_permission_scope` normalizes signed/date/scope fields.
- `compare_scope_to_intent` compares explicit permissions with distribution, territory, and duration intent.
- `escalate_for_human_review` creates a review event when records cannot establish an administrative result.

The agent orchestrates these tools and records only operational events. In Milestone 1 it runs deterministically locally so tests are repeatable. In later milestones Strands invokes Bedrock for assisted extraction; its output remains constrained to the same tool-mediated data contract. HumanInTheLoop is used for escalation approvals and document-request actions.

## Local case state (Milestone 2)

`LocalProjectStore` persists a JSON project record with item cases, received evidence, document requests, pause state, human decisions, and an ordered operation feed. `ClearanceCaseService` owns workflow transitions: its `operations_tape()` is the data source for the Operations Tape. This is a local adapter with the same seam DynamoDB will occupy later.

For the Scene 07 artwork case, the agent only records the evidence deficiency and requests human review. It pauses the case and resumes only after a human decision is recorded; it does not classify the artwork legally.

## AWS target (later)

- S3: original uploads and extracted artifacts.
- DynamoDB: projects, items, evidence links, operations, escalation state.
- Strands sessions/state: agent continuity per project.
- Amazon Bedrock: supported model through a dedicated model adapter.
- AgentCore Runtime: hosted agent execution when deployment adds value.

No AWS credentials are required for the local Milestone 1 fixture.
