# AgentOS — Enterprise Multi-Agent AI Operating System

This is the **project scaffold** for AgentOS, generated from
`Software_Architecture_Specification_v3.0_FINAL.md` (architecture frozen).

Nothing here implements agent reasoning, RAG, analytics, report
generation, or prompts — every one of those is a stub that raises
`NotImplementedError` with a `# TODO` describing exactly what goes
there. What *is* wired up: the folder structure, the `AgentState` and
`BaseAgent` contracts, the FastAPI app + routers + DB layer, and the
React app shell + routing + API service layer — so each feature can be
built one at a time without touching the plumbing around it.

## Repo layout
```
backend/    FastAPI + LangGraph + Gemini + SQLite + ChromaDB
frontend/   React + Vite + Tailwind + React Flow
docs/       architecture docs (put the frozen SAS here)
```

## Backend setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/api/v1/health`

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL defaults to localhost:8000/api/v1
npm run dev
```

App runs at `http://localhost:5173`.

## Where each SAS contract lives

| Contract (SAS section)        | File |
|---|---|
| AgentState (§5)                | `backend/schemas/agent_state.py` |
| BaseAgent (§6)                 | `backend/agents/base_agent.py` |
| Supervisor (§7)                | `backend/agents/supervisor_agent.py` |
| Specialized agents (§8)        | `backend/agents/{research,rag,analytics,document}_agent.py` |
| Memory Service (§8, no LLM)    | `backend/services/memory_service.py` |
| LangGraph workflow (§9)        | `backend/workflows/agent_workflow.py` |
| Database (§10)                 | `backend/models/`, `backend/database/` |
| Prompts (§11)                  | `backend/prompts/*_prompt.py` |
| API (§12)                      | `backend/api/v1/routes/` |
| Frontend (§13)                 | `frontend/src/pages/`, `frontend/src/layouts/` |
| Error handling (§14)           | `backend/utils/exceptions.py`, `backend/services/gemini_service.py` |
| Logging (§15)                  | `backend/utils/logger.py` |

## Build order (matches SAS §17 Development Roadmap)

Sprint 0 (this scaffold) is done. Next: Backend Foundation → Gemini →
Supervisor → Research → RAG → Document → Memory → Analytics →
Workflow → Frontend → Testing → Deployment. Implement each agent's
`validate()`/`execute()` and remove the corresponding `NotImplementedError`
one sprint at a time — the contracts here shouldn't need to change as
you go.

## Known deployment note

Render's free tier has an ephemeral filesystem — the SQLite file and
ChromaDB store under `backend/database/` will not survive a redeploy
unless you attach a persistent disk. Worth deciding before the demo,
not after.
