# ClearFrame

**Production clearance that keeps moving while your team creates.**

ClearFrame helps creative production teams track permission evidence, identify missing or incomplete documents, compare recorded permissions with intended use, and route ambiguous cases to a human reviewer. It provides evidence-led administrative support, not legal advice or a guarantee of legal clearance.

**[Open the live NIGHT SHIFT demo](https://clearframe-psi.vercel.app/)**

> **Deployment status:** The public demo uses the deterministic **local provider** because Amazon Bedrock is currently quota-blocked. The repository includes an implemented **Strands Agents SDK + Amazon Bedrock adapter**, but the public demo does **not** demonstrate live Bedrock execution.

## The problem and solution

Productions collect performer releases, archive licenses, and other permissions across many assets. A document can be present yet unsigned, out of date, or too narrow for the planned distribution. Missing evidence and unresolved questions can delay delivery.

ClearFrame turns those records into an actionable workflow: inspect evidence, flag deficiencies, request documents or corrections, pause cases that need input, and resume when new evidence or a human decision arrives. The Clearance Reel and Operations Tape show the recorded status and event history behind each result.

## Follow the NIGHT SHIFT story

NIGHT SHIFT is a fictional production seeking worldwide use on YouTube, streaming platforms, and at film festivals through January 1, 2028. Its four cases demonstrate different outcomes:

| Case | What happens |
| --- | --- |
| Sarah Cole, Scene 01 | A signed, dated performer release covers the intended use; evidence is complete. |
| Daniel Reed, Scene 02 | A missing release prompts an evidence request. An unsigned response requires correction; the signed replacement completes the evidence. |
| News Clip #03, Scene 12 | A festival-only archive license for the US and Canada, expiring in 2026, does not cover the production's intended scope. The mismatch remains visible. |
| Painting, Scene 07 | A production still cannot establish permission. The case pauses for human review; the demo records the human decision to remove the artwork from the final cut. |

Open the live demo, choose **Reset demo**, and use **Advance operation** to follow the evidence workflow. Inspect each asset and the Operations Tape, then record the artwork decision through the human-review control. **Show completed run** is a demo shortcut that supplies the scripted human decision as well as the evidence steps; it is not an autonomous legal decision.

## What the agent does

- Inspects clearance items, submitted evidence, and recorded events.
- Checks signatures, dates, and permission scope against the production's distribution, territory, and duration requirements.
- Creates evidence requests and processes incoming evidence, including correction requests for incomplete records.
- Escalates ambiguous cases, pauses them for review, and records workflow progress in an ordered audit feed.

The deployed local provider executes the fictional workflow deterministically. The Strands adapter exposes inspection, evidence-request, document-processing, and human-review tools to a Bedrock-backed agent. Both use the same application services and product rules.

## Human-review boundary

ClearFrame reports administrative evidence status. It does not determine fair use, offer legal advice, or declare a production legally safe. An evidence-complete status means the recorded evidence satisfies the configured checks.

Ambiguous cases require a recorded human decision before resuming. The Strands tool set can request review but cannot record a human decision; that action is handled separately through the API. The fictional completed-run shortcut described above is a demonstration convenience, not an approval control for real production use.

## Architecture

```text
Next.js / TypeScript Clearance Reel
                  |
              Python API
                  |
       Provider-neutral application service
                  |
        +---------+---------------------+
        |                               |
Local deterministic provider     Strands Agent + BedrockModel
(public demo)                    (implemented; quota-blocked)
        |                               |
        +-------- core workflow/tools --+
                         |
               Local JSON case state
               + fixture evidence
```

`packages/core` owns evidence evaluation and workflow transitions independently of the model provider. Adapters handle provider execution and storage. See [ARCHITECTURE.md](ARCHITECTURE.md) for the boundaries and future AWS storage/runtime targets.

## Strands + Amazon Bedrock status

`adapters/strands/provider.py` constructs a Strands `Agent` with `BedrockModel`; `adapters/strands/tools.py` defines its application-service tools. Select it explicitly with `CLEARFRAME_AGENT_PROVIDER=strands`. Model and region configuration come from environment variables, and credentials use the standard AWS credential chain or an optional named profile.

Provider errors are surfaced rather than silently falling back to local execution. Offline tests exercise the adapter with test doubles; they do not prove live Bedrock execution. Live validation requires working credentials, model access, and available Bedrock quota. S3, DynamoDB, and AgentCore Runtime remain architecture targets rather than components of the current public deployment.

## Repository structure

| Path | Purpose |
| --- | --- |
| `apps/web` | Next.js / TypeScript Clearance Reel and Operations Tape |
| `services` | HTTP API and provider-neutral application composition |
| `packages/core` | Evidence evaluation, types, state contracts, and workflow rules |
| `packages/agent_contract` | Provider and action interfaces |
| `adapters/local` | Deterministic execution, fixture evidence, and JSON persistence |
| `adapters/strands` | Strands tools, Bedrock provider, configuration, and smoke test |
| `backend` | Compatibility entry points and offline tests |
| `demo/night_shift` | Fictional records and command-line demo |
| `deploy` | API container definition; root Compose file connects both services |

## Run locally

Use Python 3.11 and Node.js 22 with npm (the versions used by the container definitions). Run these commands from a fresh checkout:

```sh
git clone https://github.com/0xBaqi/clearframe.git
cd clearframe
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS/Linux. If your system names Python `python3`, use that for the environment-creation command.

In the activated environment, start the API from the repository root:

```sh
python -m pip install -r backend/requirements.txt
python -m services.api
```

In a second terminal, from the repository root:

```sh
cd apps/web
npm install
npm run dev
```

Open [localhost:3000](http://localhost:3000). The frontend defaults to the API at `http://localhost:8000`; the API defaults to the local provider, requiring no AWS credentials. Case state is stored in `.clearframe/night-shift.json`, and **Reset demo** reseeds it.

`.env.example` lists configuration keys. Set Python API variables in the shell that starts the API; it does not automatically load a root `.env` file. For a different API URL, set `NEXT_PUBLIC_CLEARFRAME_API_URL` in `apps/web/.env.local` before starting or building the frontend. Keep `CLEARFRAME_CORS_ORIGIN` aligned with the frontend origin.

### Offline tests and command-line demo

From the repository root, using the activated Python environment:

```sh
python -m unittest discover -s backend/tests -v
python backend/run_demo.py
```

The standard suite stays offline and covers evidence checks, case transitions, API behavior, the demo loop, and the Strands adapter through test doubles.

### Optional live Bedrock smoke test

Once Bedrock quota and model access are available, configure the environment explicitly. For example, in PowerShell:

```powershell
$env:CLEARFRAME_AGENT_PROVIDER="strands"
$env:AWS_REGION="us-east-1"
$env:CLEARFRAME_BEDROCK_MODEL_ID="YOUR_ENABLED_BEDROCK_MODEL_ID"
# Optional: $env:CLEARFRAME_AWS_PROFILE="YOUR_PROFILE"
python -m adapters.strands.smoke_test
```

For AWS SSO, authenticate first with `aws sso login --profile YOUR_PROFILE`. Never commit credentials. The smoke test uses temporary state and requests read-only inspection; it is separate from the offline test suite and is not evidence of a successful run until it actually completes against Bedrock.

## Deployment note

The [public deployment](https://clearframe-psi.vercel.app/) currently uses `CLEARFRAME_AGENT_PROVIDER=local` because Bedrock is quota-blocked. The local provider demonstrates the workflow without live model calls.

For a local two-service container demo, run from the repository root:

```sh
docker compose up --build
```

This exposes the web app on port 3000 and the API on port 8000. For the same local-provider mode on a host, set `CLEARFRAME_API_HOST=0.0.0.0`, `CLEARFRAME_AGENT_PROVIDER=local`, and `CLEARFRAME_CORS_ORIGIN` to the public web origin. Build the frontend with `NEXT_PUBLIC_CLEARFRAME_API_URL` pointing to the public API. AWS credentials are unnecessary for this mode.

## License

ClearFrame is available under the [MIT License](LICENSE).
