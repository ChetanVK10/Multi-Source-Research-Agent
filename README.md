# 🔍 Multi-Source Research Agent

> **An Agentic AI Research Assistant for Grounded Knowledge Retrieval**

```{=html}
<p align="center">
```
`<strong>`{=html}Retrieve knowledge from uploaded documents and the live
web using an intelligent LangGraph
workflow.`</strong>`{=html}`<br>`{=html} Generate grounded answers with
citations and supporting evidence.
```{=html}
</p>
```
```{=html}
<p align="center">
```
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-purple?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![MIT
License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

```{=html}
</p>
```

------------------------------------------------------------------------

## 📖 Overview

**Multi-Source Research Agent** is an agentic AI application that
combines **document retrieval**, **live web search**, and **multiple LLM
providers** into a single research workflow.

Unlike traditional chatbots that rely only on model knowledge, this
system retrieves relevant information from uploaded documents and the
web, reranks the retrieved evidence using a cross-encoder model, and
synthesizes grounded responses with citations.

The workflow is orchestrated with **LangGraph**, enabling modular
reasoning and easy extensibility.

------------------------------------------------------------------------

## ✨ Features

  Feature                              Status
  ----------------------------------- --------
  PDF & TXT Upload                       ✅
  Semantic Search                        ✅
  Qdrant Vector Database                 ✅
  Live Web Search (Tavily)               ✅
  LangGraph Orchestration                ✅
  Cross-Encoder Reranking                ✅
  Multi-LLM Support (Groq & Gemini)      ✅
  Citations & Evidence                   ✅
  Conversation History                   ✅
  Document Management                    ✅
  Health Dashboard                       ✅

------------------------------------------------------------------------

## 🏗️ Architecture

``` mermaid
flowchart TD
    U[User]
    F[React + Vite Frontend]
    B[FastAPI Backend]
    G[LangGraph Workflow]
    D[Document Retriever]
    W[Web Retriever]
    Q[Qdrant]
    T[Tavily Search]
    R[Cross-Encoder Reranker]
    S[Response Synthesizer]
    L[Groq / Gemini]
    A[Grounded Answer + Citations]

    U-->F-->B-->G
    G-->D-->Q
    G-->W-->T
    D-->R
    W-->R
    R-->S-->L-->A
```

------------------------------------------------------------------------

## 🔄 LangGraph Workflow

``` text
User Query
    │
 Planner
    │
 Router
 ┌──┴─────────┐
 │            │
Document   Web Search
Retriever  Retriever
 │            │
 └─────┬──────┘
       │
 Evidence Merge
       │
Cross-Encoder Reranker
       │
 Response Synthesizer
       │
Final Answer + Citations
```

------------------------------------------------------------------------

## 🛠️ Tech Stack

### Frontend

-   React
-   TypeScript
-   Vite

### Backend

-   FastAPI
-   LangGraph

### AI

-   Groq
-   Gemini
-   BAAI/bge-small-en-v1.5 Embeddings
-   Cross-Encoder Reranker

### Retrieval

-   Qdrant
-   Tavily Search

### Storage

-   SQLite

### Deployment

-   Docker

------------------------------------------------------------------------

## 📂 Project Structure

``` text
backend/
 ├── app/
 │   ├── api/
 │   ├── graph/
 │   ├── services/
 │   └── models/

frontend/
 ├── src/
 │   ├── components/
 │   ├── hooks/
 │   ├── pages/
 │   └── services/

docs/
infra/
docker-compose.yml
README.md
```

------------------------------------------------------------------------

## 🚀 Installation

``` bash
git clone https://github.com/<username>/Multi-Source-Research-Agent.git
cd Multi-Source-Research-Agent
```

### Backend

``` bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### Frontend

``` bash
cd frontend
npm install
```

### Start Qdrant

``` bash
docker compose up -d qdrant
```

------------------------------------------------------------------------

## 🔑 Environment Variables

Create a `.env` file:

``` env
GROQ_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

DEFAULT_PROVIDER=groq
FALLBACK_PROVIDER=gemini
```

------------------------------------------------------------------------

## ▶️ Run the Project

``` bash
# Backend
uvicorn app.main:app --reload

# Frontend
npm run dev
```

------------------------------------------------------------------------

## 💬 Example Queries

-   Summarize this uploaded research paper.
-   Compare the uploaded documents.
-   Explain Retrieval-Augmented Generation.
-   Search the web for the latest AI developments.
-   List the certifications mentioned in my resume.

------------------------------------------------------------------------

## 🌐 API Endpoints

  Method   Endpoint              Description
  -------- --------------------- -----------------------
  POST     `/chat`               Submit research query
  POST     `/documents/upload`   Upload documents
  GET      `/documents`          List documents
  DELETE   `/documents/{id}`     Delete document
  GET      `/health`             Service health
  GET      `/models`             Available LLMs

------------------------------------------------------------------------

## 🛣️ Roadmap

-   [x] Document Retrieval
-   [x] Live Web Search
-   [x] Multi-LLM Support
-   [x] Citations & Evidence
-   [x] Health Dashboard
-   [ ] Streaming Responses
-   [ ] Authentication
-   [ ] MCP Integrations
-   [ ] Cloud Deployment

------------------------------------------------------------------------

## 📸 Screenshots

> Screenshots and demo GIF will be added in the next release.

------------------------------------------------------------------------

## 📄 License

This project is licensed under the **MIT License**.

------------------------------------------------------------------------

## 👨‍💻 Author

**Chetan VK**

B.Tech -- Artificial Intelligence & Data Science

If you found this project useful, consider giving it a ⭐ on GitHub.
