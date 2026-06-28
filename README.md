# Multi-Source Research Agent

Production-ready GenAI research system that plans source usage, retrieves evidence from multiple sources, reranks evidence, and synthesizes grounded answers with citations.

## Architecture

```text
User Query
  |
  v
FastAPI API Layer
  |
  v
Planner Node
  |
  v
Conditional Router
  |
  +--> Documents Retrieval -> Qdrant
  |
  +--> Web Retrieval -------> Tavily Search API
  |
  +--> SQL Retrieval --------> PostgreSQL
  |
  v
Merge Node
  |
  v
Cross-Encoder Reranker Node
  |
  v
Synthesizer Node
  |
  v
Final Answer + Citations
```

Phase 1 includes the project structure, backend configuration, environment management, FastAPI setup, and LangGraph state definition.

Phase 2 adds the planner node, router node, and LangGraph workflow.

Phase 3 adds Qdrant integration, Gemini embeddings, document ingestion, chunking, upload, indexing, and document retrieval.

Phase 4 adds a web search tool wrapper, Tavily integration, web evidence normalization, web retrieval node, and recoverable tool error handling.

Phase 5 adds PostgreSQL integration, constrained SQL query generation, validation guardrails, execution, and SQL evidence retrieval.

Phase 6 adds evidence merging, cross-encoder reranking, lexical fallback reranking, and top-k context selection.

Phase 7 adds grounded answer synthesis, citation generation, inline citation enforcement, and insufficient-evidence handling.

## Project Structure

```text
multi-source-research-agent/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- v1/
|   |   |   |   |-- routes/
|   |   |   |   |   |-- chat.py
|   |   |   |   |   |-- documents.py
|   |   |   |   |   |-- health.py
|   |   |   |   |-- router.py
|   |   |   |-- deps.py
|   |   |-- core/
|   |   |   |-- config.py
|   |   |   |-- errors.py
|   |   |   |-- logging.py
|   |   |-- graph/
|   |   |   |-- architecture.py
|   |   |   |-- builder.py
|   |   |   |-- nodes/
|   |   |   |   |-- document_retriever.py
|   |   |   |   |-- merge.py
|   |   |   |   |-- planner.py
|   |   |   |   |-- reranker.py
|   |   |   |   |-- router.py
|   |   |   |   |-- sql_retriever.py
|   |   |   |   |-- synthesizer.py
|   |   |   |   |-- web_retriever.py
|   |   |   |-- state.py
|   |   |-- ingestion/
|   |   |   |-- chunking.py
|   |   |   |-- loaders.py
|   |   |   |-- pipeline.py
|   |   |-- models/
|   |   |   |-- citations.py
|   |   |   |-- documents.py
|   |   |   |-- evidence.py
|   |   |   |-- requests.py
|   |   |   |-- responses.py
|   |   |   |-- sql.py
|   |   |   |-- synthesis.py
|   |   |   |-- web.py
|   |   |-- services/
|   |   |   |-- embeddings/
|   |   |   |   |-- embedding_service.py
|   |   |   |-- llm/
|   |   |   |   |-- gemini_client.py
|   |   |   |   |-- prompts.py
|   |   |   |-- synthesis/
|   |   |   |   |-- citations.py
|   |   |   |   |-- synthesizer.py
|   |   |   |-- vectorstore/
|   |   |   |   |-- document_indexer.py
|   |   |   |   |-- factory.py
|   |   |   |   |-- qdrant_client.py
|   |   |   |-- web/
|   |   |   |   |-- factory.py
|   |   |   |   |-- retriever.py
|   |   |   |   |-- search_tool.py
|   |   |   |   |-- tavily_tool.py
|   |   |   |-- sql/
|   |   |   |   |-- db.py
|   |   |   |   |-- factory.py
|   |   |   |   |-- query_generator.py
|   |   |   |   |-- retriever.py
|   |   |   |   |-- validator.py
|   |   |   |-- reranking/
|   |   |   |   |-- reranker.py
|   |   |-- utils/
|   |   |   |-- ids.py
|   |   |-- main.py
|   |-- tests/
|   |-- Dockerfile
|   |-- pyproject.toml
|   |-- README.md
|-- frontend/
|   |-- src/
|   |-- README.md
|-- infra/
|   |-- env/
|   |   |-- backend.env.example
|   |   |-- frontend.env.example
|   |-- render/
|   |   |-- render.yaml
|-- docs/
|   |-- architecture.md
|-- docker-compose.yml
|-- README.md
```

# MANUAL CHANGES REQUIRED

## API Keys

- Create a Google Gemini API key.
- Create a LangSmith API key.
- Create a Tavily API key for Phase 4 web retrieval.
- Create a Qdrant API key if using Qdrant Cloud.
- Phase 3 requires `GEMINI_API_KEY` for document embeddings.
- Phase 4 requires `WEB_SEARCH_API_KEY` when the planner routes a query to web search.
- Phase 5 does not require a new API key, but it requires PostgreSQL credentials in `DATABASE_URL`.
- Phase 6 may download the configured cross-encoder model from Hugging Face during first runtime use.
- Phase 7 requires `GEMINI_API_KEY` for model-based answer synthesis. If Gemini is unavailable, the system returns extractive grounded snippets instead of guessing.

## Environment Variables

Copy `infra/env/backend.env.example` into a local backend `.env` file before running the backend.

Required backend variables:

- `APP_ENV`
- `APP_NAME`
- `API_V1_PREFIX`
- `BACKEND_CORS_ORIGINS`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_EMBEDDING_MODEL`
- `GEMINI_TEMPERATURE`
- `LANGSMITH_TRACING`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION_NAME`
- `QDRANT_VECTOR_SIZE`
- `QDRANT_DISTANCE_METRIC`
- `DOCUMENT_CHUNK_SIZE`
- `DOCUMENT_CHUNK_OVERLAP`
- `DOCUMENT_RETRIEVAL_TOP_K`
- `DATABASE_URL`
- `SQL_ALLOWED_TABLES`
- `SQL_DEFAULT_TABLE`
- `SQL_RESULT_LIMIT`
- `SQL_STATEMENT_TIMEOUT_MS`
- `WEB_SEARCH_PROVIDER`
- `WEB_SEARCH_API_KEY`
- `WEB_SEARCH_TOP_K`
- `WEB_SEARCH_TIMEOUT_SECONDS`
- `RERANKER_MODEL_NAME`
- `RERANKER_TOP_K`
- `RERANKER_BATCH_SIZE`
- `RERANKER_FALLBACK_ENABLED`
- `SYNTHESIS_MAX_CONTEXT_CHARS`
- `SYNTHESIS_REQUIRE_CITATIONS`

Required frontend variables:

- `VITE_API_BASE_URL`

## MCP Configuration

No MCP server is required for Phase 5.

Web search currently uses the Tavily HTTP API directly through an internal tool wrapper. If Tavily is later replaced with an MCP search server, update the web tool factory and deployment configuration.

Later phases may require MCP configuration for:

- Document or filesystem access

## Deployment Configuration

Render configuration in `infra/render/render.yaml` is a placeholder and must be reviewed before production deployment.

Manual deployment edits required:

- Backend service name
- Frontend service name
- Environment variables
- Build commands
- Start commands
- Region
- Instance size
- Persistent database and vector database strategy
- Tavily API key secret
- PostgreSQL credentials
- Cross-encoder model download/cache strategy
- Gemini API key secret

## Database Setup

SQL retrieval is implemented in Phase 5.

Required setup:

- Provision a SQL database.
- Create application tables.
- Configure `DATABASE_URL`.
- Prefer read-only credentials for agent query execution.
- Set `SQL_ALLOWED_TABLES` to a comma-separated allowlist of tables the agent may query.
- Optionally set `SQL_DEFAULT_TABLE` to bias query generation.
- Tune `SQL_RESULT_LIMIT`.
- Tune `SQL_STATEMENT_TIMEOUT_MS`.
- Add migrations once the schema is finalized.

The SQL retriever only generates and validates read-only `SELECT` statements. Destructive SQL keywords are blocked, and referenced tables must be present in `SQL_ALLOWED_TABLES`.

## Vector Database Setup

Qdrant retrieval is implemented in Phase 3.

Required setup:

- Provision Qdrant Cloud or a self-hosted Qdrant instance.
- Set `QDRANT_URL`.
- Set `QDRANT_API_KEY` if using Qdrant Cloud.
- Set `QDRANT_COLLECTION_NAME`.
- Match `QDRANT_VECTOR_SIZE` to `GEMINI_EMBEDDING_MODEL`.
- Keep `QDRANT_DISTANCE_METRIC=Cosine` unless there is a model-specific reason to change it.
- Upload `.txt`, `.md`, or `.pdf` files through `/api/v1/documents/upload`.

## Web Search Setup

Web retrieval is implemented in Phase 4.

Required setup:

- Create a Tavily API key.
- Set `WEB_SEARCH_PROVIDER=tavily`.
- Set `WEB_SEARCH_API_KEY`.
- Tune `WEB_SEARCH_TOP_K` for the desired number of web results.
- Tune `WEB_SEARCH_TIMEOUT_SECONDS` for deployment latency tolerance.

## Reranker Setup

Cross-encoder reranking is implemented in Phase 6.

Required setup:

- Set `RERANKER_MODEL_NAME`.
- Keep `RERANKER_FALLBACK_ENABLED=true` if the app should continue with lexical ranking when the cross-encoder is unavailable.
- Tune `RERANKER_TOP_K` for the number of evidence chunks passed to synthesis.
- Tune `RERANKER_BATCH_SIZE` based on CPU/RAM limits.
- Ensure the deployment environment can download/cache the sentence-transformers model, or pre-bake the model into the Docker image in a later production hardening phase.

## Synthesis Setup

Grounded answer synthesis is implemented in Phase 7.

Required setup:

- Set `GEMINI_API_KEY`.
- Set `GEMINI_MODEL`.
- Keep `GEMINI_TEMPERATURE` low for factual synthesis.
- Tune `SYNTHESIS_MAX_CONTEXT_CHARS` to control context size and latency.
- Keep `SYNTHESIS_REQUIRE_CITATIONS=true` for production.

## Multi-Provider LLM Setup & Registry

The system supports dynamically selecting the LLM provider and model for grounded answer synthesis from the frontend UI.

### Providers & Models
- **Gemini**: `gemini-2.5-flash`, `gemini-2.5-pro`
- **Groq**: `llama-3.3-70b-versatile`, `deepseek-r1-distill-llama-70b`, `qwen-qwq-32b`

### Environment Variables
Configure the following options in your backend `.env` file:
- `GROQ_API_KEY`: API key for Groq synthesis.
- `DEFAULT_PROVIDER`: Default primary provider (e.g. `gemini`).
- `DEFAULT_MODEL`: Default primary model (e.g. `gemini-2.5-flash`).
- `FALLBACK_PROVIDER`: Fallback provider (e.g. `groq`).
- `FALLBACK_MODEL`: Fallback model (e.g. `llama-3.3-70b-versatile`).

### Graceful Fallback Strategy
- **Configuration Fallback**: If a selected provider's credentials are not configured at runtime, the initialization immediately routes to the secondary provider/model.
- **Runtime Fallback**: If the primary client call raises an exception (e.g. rate limit, API outage), the client wrapper catches the error and executes the query using the fallback client.
- **Observability**: The actually used provider and model are tracked in the LangGraph state, returned in the REST API chat response payload, and rendered in assistant chat message bubbles.

Hallucination reduction behavior:

- The synthesizer receives only reranked evidence.
- Citations are generated from retrieved evidence, not model output.
- Invalid citation IDs are stripped from the answer.
- If no evidence is available, the system returns an insufficient-evidence answer.
- If Gemini fails, the system returns extractive snippets from evidence with citations.

## Manual Edits

Before production use, review:

- CORS origins
- Authentication and authorization
- Rate limits
- Upload size limits
- Logging level
- LangSmith project name
- Render service configuration
- Secret management strategy
- Web search result usage and compliance requirements
- Reranker model licensing, memory footprint, and cold-start time
- Gemini model cost, latency, quota, and safety settings

# Frontend Setup

The `frontend/` app is a React, TypeScript, Vite, Tailwind CSS, Axios, and React Query dashboard for the existing FastAPI backend.

```bash
cd frontend
npm install
npm run dev
npm run build
```

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Backend connection defaults:

- FastAPI base URL: `http://localhost:8000`
- API v1 prefix: `/api/v1`
- Frontend API base URL: `http://localhost:8000/api/v1`

Connected frontend routes:

- Research chat uses `POST /chat`
- Document upload uses `POST /documents/upload`
- Health dashboard uses `GET /health`
- Trace viewer is wired to placeholder `GET /trace`

# Manual Changes Required

- Set `VITE_API_BASE_URL` in `frontend/.env` for local, staging, or production.
- Keep `BACKEND_CORS_ORIGINS` aligned with the deployed frontend origin.
- Add a backend `/api/v1/trace` endpoint when LangGraph trace data is ready to expose.
- Add dedicated backend health probes if the UI should report live Qdrant, PostgreSQL, and LangSmith status independently.
