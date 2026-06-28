# Backend

FastAPI backend for the Multi-Source Research Agent.

Phase 1 provides:

- Typed environment management
- Structured logging setup
- FastAPI application shell
- Versioned API router
- Health endpoint
- Chat endpoint placeholder
- Shared request/response models
- LangGraph state definition

Retrieval nodes are intentionally not implemented in this phase.

## Local Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Environment

Create a local `.env` file using `../infra/env/backend.env.example` as a template.
