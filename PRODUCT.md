# ClearFrame V1

## Purpose

ClearFrame is a clearance-operations workspace for independent creative teams. It turns project materials into an evidence-led clearance register: what is evidenced, missing, restricted, inconsistent, or needs human review.

It is **not** legal advice. It does not decide fair use, assess legal risk, or declare a project safe for release. When records need legal interpretation, it presents the evidence and routes the item to a person.

## V1 users and workflow

A producer creates a project, describes intended distribution and territories, then uploads or connects production records. ClearFrame identifies clearance items, links supporting records, compares stated permissions to the project’s declared intent, and records its operations.

The V1 demo project is **NIGHT SHIFT**, a fictional short film intended for YouTube, streaming platforms, and festivals worldwide.

Supported categories:

- Performer / appearance
- Location
- Music
- Artwork / image
- Archive footage

## Milestone 1 acceptance criteria

The local agent ingests the seeded NIGHT SHIFT records and derives, via evidence-reading and scope-comparison tools:

| Clearance item | Expected status |
| --- | --- |
| Sarah Cole | `EVIDENCE_COMPLETE` |
| Daniel Reed | `EVIDENCE_MISSING` |
| News Clip #03 | `SCOPE_MISMATCH` |
| Painting in Scene 7 | `HUMAN_REVIEW` |

Every output includes an evidence chain and operations-tape events. Results are not a static report: changing the seed records changes the tool-derived outcome.

## Later milestones (out of scope now)

1. Upload intake, S3 storage, document extraction, and a project workspace.
2. DynamoDB persistence, Strands sessions/state, and Bedrock-supported assisted extraction.
3. AgentCore Runtime deployment.
