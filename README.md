# Campus Customs — Homework 4

This repository contains the Campus Customs storefront, FastAPI/PydanticAI backend, database harness, design notes, and Problem 11 app-check evidence.

## Local-only data pack

The public repository intentionally does not contain the database or product photos. Before running the app, place the supplied local data pack at this exact layout:

```text
hw4/
├── data/
│   ├── campus_customs.db
│   └── products/
│       └── <catalogue image files>
```

The image filenames must match the `image_file_path` values in `catalogue`. Do not commit this folder, `.env`, or API keys.

## Configuration

Copy `.env.example` to `.env` and add your own `PORTKEY_API_KEY`. Keep the real `.env` local. The backend uses `gpt-5.6-luna` by default and accepts `PORTKEY_MODEL` as an override.

## Run the backend

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The backend reads `../data/campus_customs.db`, serves catalogue and authentication routes, and loads the agent from these four files:

```text
backend/agent.py
backend/tools.py
backend/models.py
backend/prompts/prompts.md
```

## Run the frontend

In a second terminal, from `frontend/`:

```bash
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`. The export step reads the local data pack and generates the catalogue data plus image assets before Vite starts. For a server-independent hand-in build, run `npm run build:standalone`; the generated `frontend/dist/index.html` is local and ignored by Git.

## Deliverables

`AI_prompts.md` records the prompts by problem. `output/harness.md` documents the database, API, agent, tools, safety limits, and launch commands. `output/app_check.html` is a double-clickable Problem 11 report with relative links to its current screenshots. `output/audit_trail.json` is append-only agent-loop evidence.
