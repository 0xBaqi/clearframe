# ClearFrame

Evidence-led administrative clearance operations for creative productions. Not legal advice.

## Milestone 1

The repository contains a Next.js Clearance Reel prototype and a local Python Strands-compatible agent fixture for the fictional **NIGHT SHIFT** project.

### Run the agent tests

```powershell
& 'C:\\Users\\NURUDEEN\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' -m unittest discover -s backend/tests -v
```

### Run the agent demo

```powershell
& 'C:\\Users\\NURUDEEN\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' backend/run_demo.py
```

### Run the web prototype

```powershell
npm install
npm run dev
```

The web view currently renders the same fictional seed state. Connecting it to the agent API is a later milestone.

Install the backend dependency with `pip install -r backend/requirements.txt` when preparing a dedicated Python environment. The deterministic run is intentionally offline; it exercises the same evidence-tool boundary that a Bedrock-powered Strands run will use after AWS configuration.
