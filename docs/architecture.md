# Architecture

The Multi-Source Research Agent uses FastAPI for the API layer and LangGraph for explicit research workflow orchestration.

## Phase 1 Scope

Implemented:

- FastAPI application factory
- Versioned API router
- Health endpoint
- Chat endpoint placeholder
- Typed environment settings
- Structured logging setup
- Shared Pydantic models
- LangGraph state schema

## Phase 2 Scope

Implemented:

- Planner node
- Router node
- Compilable LangGraph workflow
- Conditional branch selection
- Placeholder branch nodes for future document, web, and SQL retrieval
- Chat endpoint integration with the graph

## Phase 3 Scope

Implemented:

- Gemini embedding service
- Qdrant async client integration
- Qdrant collection creation
- Text and PDF document loading
- Configurable chunking pipeline
- Document indexing into Qdrant
- Document upload API
- Document retrieval graph node

## Phase 4 Scope

Implemented:

- Web search tool wrapper
- Tavily web search provider
- Web result normalization
- Web retrieval service
- Web retrieval graph node
- Recoverable web tool error handling

## Phase 5 Scope

Implemented:

- PostgreSQL integration
- SQL schema inspection for allowlisted tables
- Constrained SQL query generation
- SQL validation guardrails
- SQL retrieval service
- SQL retrieval graph node
- Recoverable SQL execution error handling

## Phase 6 Scope

Implemented:

- Merge node
- Evidence deduplication
- Cross-encoder reranking service
- Lexical fallback reranker
- Top-k context selection
- Reranked evidence returned by the chat endpoint

## Phase 7 Scope

Implemented:

- Synthesizer node
- Gemini chat client wrapper
- Grounded synthesis prompt
- Citation generation from evidence
- Inline citation enforcement
- Insufficient-evidence responses
- Extractive fallback synthesis

Deferred:

- Frontend implementation

## Graph State

`ResearchGraphState` is the shared contract passed between LangGraph nodes. It carries the original query, planner decision, per-source evidence, merged evidence, reranked evidence, final answer, and recoverable graph errors.

Graph errors use an additive reducer so parallel retrieval branches can report recoverable failures without overwriting each other.

## Current Graph

```text
User Query
  |
  v
FastAPI /api/v1/chat
  |
  v
Planner Node
  |
  v
Router Node
  |
  +--> Document Retriever Node -> Gemini Query Embedding -> Qdrant
  |
  +--> Web Retriever Node ------> Tavily Search API
  |
  +--> SQL Retriever Node ------> PostgreSQL
  |
  v
Merge Node
  |
  v
Cross-Encoder Reranker Node
  |
  v
Top-k Evidence
  |
  v
Synthesizer Node
  |
  v
Grounded Answer + Citations
```

The router uses the planner decision to choose only the required branches. The document branch performs Qdrant retrieval. The web branch performs Tavily search through a tool wrapper. The SQL branch performs validated read-only PostgreSQL retrieval.

## Phase 3 Document Flow

```text
Upload Document
  |
  v
FastAPI /api/v1/documents/upload
  |
  v
Loader (.txt / .md / .pdf)
  |
  v
Chunker
  |
  v
Gemini Embeddings
  |
  v
Qdrant Collection
```

```text
Query routed to documents
  |
  v
Document Retriever Node
  |
  v
Gemini Query Embedding
  |
  v
Qdrant Similarity Search
  |
  v
Document Evidence
```

## Phase 4 Web Flow

```text
Query routed to web
  |
  v
Web Retriever Node
  |
  v
Web Search Tool Wrapper
  |
  v
Tavily Search API
  |
  v
Normalized Web Evidence
```

## Phase 5 SQL Flow

```text
Query routed to SQL
  |
  v
SQL Retriever Node
  |
  v
Load allowlisted PostgreSQL schema
  |
  v
Constrained query generation
  |
  v
SQL validation
  |
  v
Parameterized PostgreSQL execution
  |
  v
SQL Evidence
```

The SQL validator only allows single read-only `SELECT` statements. It blocks common destructive keywords and rejects references to tables outside `SQL_ALLOWED_TABLES`.

## Phase 6 Ranking Flow

```text
Document Evidence
Web Evidence
SQL Evidence
  |
  v
Merge Node
  |
  v
Deduplicate by URL or evidence ID
  |
  v
Cross-Encoder Reranker
  |
  v
Top-k Reranked Evidence
```

If the cross-encoder model cannot be loaded or executed, the graph records a recoverable error and uses lexical fallback reranking when `RERANKER_FALLBACK_ENABLED=true`.

## Phase 7 Synthesis Flow

```text
Top-k Reranked Evidence
  |
  v
Citation Builder
  |
  v
Grounded Prompt
  |
  v
Gemini
  |
  v
Citation Enforcement
  |
  v
Final Answer + Citations
```

The synthesizer is designed to reduce hallucinations by giving the model only selected evidence, requiring inline citation IDs, stripping invalid citation IDs, and returning an explicit insufficient-evidence message when no context is available.
