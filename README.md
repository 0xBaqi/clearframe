# ClearFrame

Evidence-led administrative clearance operations for creative productions. Not legal advice.

## Milestone 1

The repository contains a Next.js Clearance Reel prototype and a local Python agent fixture for the fictional **NIGHT SHIFT** project. Product logic is provider-agnostic; the Strands adapter is replaceable.

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

Install the backend dependency with `pip install -r backend/requirements.txt` when preparing a dedicated Python environment. The deterministic run is intentionally offline; a dedicated Strands adapter owns future Bedrock integration without changing product rules.

## Optional Strands / Bedrock smoke test

Copy `.env.example` and set `CLEARFRAME_AGENT_PROVIDER=strands`, `AWS_REGION`, and a Bedrock model ID. Credentials come from the normal AWS credential chain or the optional `CLEARFRAME_AWS_PROFILE`; never place credentials in the repository. With model access enabled, run `python -m adapters.strands.smoke_test`. This test is optional and the standard suite stays offline.
