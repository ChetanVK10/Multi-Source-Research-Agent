# 🔍 Multi-Source Research Agent

> **An Agentic AI Research Assistant for Grounded Knowledge Retrieval**

<p align="center">
  <strong>
    Retrieve knowledge from uploaded documents and the live web using an intelligent LangGraph workflow.
  </strong>
  <br>
  Generate grounded answers with citations and supporting evidence.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-purple?style=for-the-badge)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</p>

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

| Feature | Status |
|---------|:------:|
| PDF & TXT Upload | ✅ |
| Semantic Search | ✅ |
| Qdrant Vector Database | ✅ |
| Live Web Search (Tavily) | ✅ |
| LangGraph Orchestration | ✅ |
| Cross-Encoder Reranking | ✅ |
| Multi-LLM Support (Groq & Gemini) | ✅ |
| Citations & Evidence | ✅ |
| Conversation History | ✅ |
| Document Management | ✅ |
| Health Dashboard | ✅ |

------------------------------------------------------------------------

## 📸 Screenshots

<table>
  <tr>
    <td align="center"><b>Research Workspace</b></td>
    <td align="center"><b>Document Upload</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/home.png" alt="Research Workspace" width="500"/></td>
    <td><img src="screenshots/upload.png" alt="Document Upload" width="500"/></td>
  </tr>

  <tr>
    <td align="center"><b>Document Management</b></td>
    <td align="center"><b>System Health</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/documents.png" alt="Document Management" width="500"/></td>
    <td><img src="screenshots/health.png" alt="System Health" width="500"/></td>
  </tr>

  <tr>
    <td align="center"><b>Resume Analysis</b></td>
    <td align="center"><b>Research Paper Analysis</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/resume.png" alt="Resume Analysis" width="500"/></td>
    <td><img src="screenshots/paper.png" alt="Research Paper Analysis" width="500"/></td>
  </tr>

  <tr>
    <td align="center"><b>Annual Report Analysis</b></td>
    <td align="center"><b>Live Web Search</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/report.png" alt="Annual Report Analysis" width="500"/></td>
    <td><img src="screenshots/web-search.png" alt="Live Web Search" width="500"/></td>
  </tr>
</table>

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
git clone https://github.com/ChetanVK10/Multi-Source-Research-Agent.git
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Submit research query |
| POST | `/documents/upload` | Upload documents |
| GET | `/documents` | List uploaded documents |
| DELETE | `/documents/{id}` | Delete a document |
| GET | `/health` | Backend health status |
| GET | `/models` | Available LLM providers |

------------------------------------------------------------------------

## 📄 License

This project is licensed under the **MIT License**.

------------------------------------------------------------------------

## 👨‍💻 Author

**Chetan VK**

B.Tech -- Artificial Intelligence & Data Science

If you found this project useful, consider giving it a ⭐ on GitHub.
