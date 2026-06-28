# Multi-Source Research Agent Frontend

Production React interface for the existing FastAPI, LangGraph, Qdrant, Tavily, PostgreSQL, reranking, synthesis, and citation backend.

## Frontend Setup

```bash
npm install
npm run dev
npm run build
npm run preview
```

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

The frontend uses:

- React + TypeScript + Vite
- Tailwind CSS
- Axios
- React Query
- React Router
- Lucide icons

## Backend Connection Setup

Start the backend first, then point `VITE_API_BASE_URL` at the API v1 prefix. With the current backend defaults, that is:

```bash
http://localhost:8000/api/v1
```

Connected endpoints:

- `POST /chat`
- `POST /documents/upload`
- `GET /health`

Placeholder endpoint:

- `GET /trace`

The trace page calls the real `/trace` endpoint. It does not use mock data, so it will show an endpoint-unavailable state until the backend exposes traces.

## Manual Changes Required

- Add `frontend/.env` with `VITE_API_BASE_URL`.
- Ensure backend CORS allows the Vite origin, usually `http://localhost:5173`.
- Confirm the upload route remains `/api/v1/documents/upload`.
- Add a backend `/api/v1/trace` route when graph traces are ready to expose.
- Replace placeholder dependent-service health assumptions with dedicated Qdrant, PostgreSQL, and LangSmith probes if those endpoints are added later.
