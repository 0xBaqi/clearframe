# ClearFrame architecture

## Provider-agnostic boundary

The frontend is a Next.js + TypeScript application. The agent service is Python. `packages/core` owns product rules and has no dependency on Strands, Bedrock, AWS, Gemini, Nebius, or any other provider. The frontend consumes a product-facing API contract; it never depends directly on a model or agent framework.

```
Next.js Clearance Reel
        │
        ▼
ClearFrame API contract
        │
        ▼
Agent-provider contract ──► provider adapter ──► core evidence tools ──► record/file adapters
        │                                │
        │                                ├─ local fixture evidence / JSON state (current)
        │                                ├─ S3 (later)
        │                                └─ DynamoDB (later state)
        ▼
Strands adapter ──► Amazon Bedrock (implemented; quota-blocked)
                   AgentCore Runtime (future deployment target)
```

## Package boundaries

- `packages/core`: statuses, types, evidence comparison, operations, case transitions, and workflow rules.
- `packages/agent_contract`: provider interface used by product services.
- `adapters/local`: JSON state and in-memory evidence implementations.
- `adapters/strands`: the sole Strands-facing provider boundary.
- `services/agent`: provider-neutral application composition.
- `demo/night_shift`: fictional fixture data only.

## Adapter rule

`AgentProvider` is the provider interface. It accepts a project intent and returns clearance results. A Strands, Gemini, Nebius, or another implementation can satisfy it without changing statuses, tools, frontend contracts, persistence models, or workflow rules.

## Agent design

The tool layer owns facts:

- `list_clearance_items` identifies the records to review.
- `find_evidence` returns submitted records for an item.
- `read_permission_scope` normalizes signed/date/scope fields.
- `compare_scope_to_intent` compares explicit permissions with distribution, territory, and duration intent.
- `escalate_for_human_review` creates a review event when records cannot establish an administrative result.

The agent orchestrates these tools and records operational events. The current public deployment uses the deterministic local provider because Bedrock is quota-blocked; it does not execute live Bedrock calls. The implemented Strands adapter constructs a Strands Agent with BedrockModel when explicitly configured and exposes inspection, evidence-request, document-processing, and human-review tools through the application service. Provider errors are surfaced without silent fallback. Human decisions are handled separately through the API, not exposed as Strands tools. The completed-run demo shortcut supplies a scripted human decision.

## Local case state

`LocalProjectStore` persists a JSON project record with item cases, received evidence, document requests, pause state, human decisions, and an ordered operation feed. `ClearanceCaseService` owns workflow transitions: its `operations_tape()` is the data source for the Operations Tape. This is a local adapter with the same seam DynamoDB will occupy later.

For the Scene 07 artwork case, the agent only records the evidence deficiency and requests human review. It pauses the case and resumes only after a human decision is recorded; it does not classify the artwork legally.

## AWS target (when Bedrock capacity is available)

- S3: original uploads and extracted artifacts.
- DynamoDB: projects, items, evidence links, operations, escalation state.
- Strands sessions/state: agent continuity per project.
- Amazon Bedrock: supported model through a dedicated model adapter.
- AgentCore Runtime: hosted agent execution when deployment adds value.

No AWS credentials are required for the current local-provider demo. The Bedrock adapter is implemented, but live execution requires available quota and model access. S3, DynamoDB, Strands sessions/state, and AgentCore Runtime above are future targets, not claims about the current public deployment.
