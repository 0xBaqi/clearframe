# ClearFrame

Evidence-led administrative clearance operations for creative productions. Not legal advice.

## Current build

The repository contains the frozen V3.1 Next.js Clearance Reel and a Python application service for the fictional **NIGHT SHIFT** project. Product logic is provider-agnostic: the deterministic local provider is the offline default, while the implemented Strands adapter is selected only when Bedrock is configured.

### Run the agent tests

```powershell
& 'C:\\Users\\NURUDEEN\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' -m unittest discover -s backend/tests -v
```

### Run the agent demo

```powershell
& 'C:\\Users\\NURUDEEN\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' backend/run_demo.py
```

### Run the local demo

Start the provider-neutral API first (it uses the local deterministic provider by default):

```powershell
python -m services.api
```

Then start the web app in a second terminal:

```powershell
cd apps/web
npm install
npm run dev
```

The web app reads project state and the global production audit from `http://localhost:8000` by default. Copy `.env.example` to configure `NEXT_PUBLIC_CLEARFRAME_API_URL`, the API port, or the CORS origin for local development. The API persists the NIGHT SHIFT state in `.clearframe/night-shift.json`; **Reset demo** safely reseeds it.

Install the backend dependency with `pip install -r backend/requirements.txt` when preparing a dedicated Python environment. The deterministic run is intentionally offline; the dedicated Strands adapter owns the implemented Bedrock integration without changing product rules.

## Minimal deployment path

The repository includes a deliberately small two-service container setup for the offline demo:

```powershell
docker compose up --build
```

It serves the web experience at `http://localhost:3000` and the local-provider API at `http://localhost:8000`. For a public deployment, deploy the API with `CLEARFRAME_AGENT_PROVIDER=local`, `CLEARFRAME_API_HOST=0.0.0.0`, and `CLEARFRAME_CORS_ORIGIN` set to the public web origin. Build the web service with `NEXT_PUBLIC_CLEARFRAME_API_URL` set to that API's public URL. Do not provide AWS credentials in the deployment while Bedrock throttling is pending.

## Optional Strands / Bedrock smoke test

Copy `.env.example` and set `CLEARFRAME_AGENT_PROVIDER=strands`, `AWS_REGION`, and a Bedrock model ID. Credentials come from the normal AWS credential chain or the optional `CLEARFRAME_AWS_PROFILE`; never place credentials in the repository. With model access enabled, run `python -m adapters.strands.smoke_test`. This test is optional and the standard suite stays offline.

In PowerShell, an AWS SSO setup can authenticate with `aws sso login --profile YOUR_PROFILE`. Then select any Bedrock model enabled for your account without changing code:

```powershell
$env:CLEARFRAME_AGENT_PROVIDER="strands"
$env:AWS_REGION="us-east-1"
$env:CLEARFRAME_BEDROCK_MODEL_ID="YOUR_ENABLED_BEDROCK_MODEL_ID"
# Optional: $env:CLEARFRAME_AWS_PROFILE="YOUR_PROFILE"
python -m adapters.strands.smoke_test
python -m services.api
```

The Strands agent has inspection, evidence-request, document-processing, and human-review tools. Human decisions remain API-only. Provider failures are surfaced to the API; they never silently fall back to the local provider.
