from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes import documents
from app.core.config import Settings, get_settings
from app.models.documents import DocumentChunk


class FakeIndexer:
    def __init__(self) -> None:
        self.indexed_chunks: list[DocumentChunk] = []

    async def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.indexed_chunks.extend(chunks)


@pytest.fixture()
def fake_indexer() -> FakeIndexer:
    return FakeIndexer()


@pytest.fixture()
def client(fake_indexer: FakeIndexer, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(documents.router, prefix="/documents")
    app.dependency_overrides[get_settings] = lambda: Settings(
        gemini_api_key="test",
        qdrant_url="http://localhost:6333",
        document_chunk_size=40,
        document_chunk_overlap=5,
    )
    monkeypatch.setattr(documents, "build_document_indexer", lambda settings: fake_indexer)

    with TestClient(app) as test_client:
        yield test_client


def test_openapi_upload_schema_uses_binary_file_array(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    request_body_ref = schema["paths"]["/documents/upload"]["post"]["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]["$ref"]
    schema_name = request_body_ref.rsplit("/", 1)[-1]
    files_schema = schema["components"]["schemas"][schema_name]["properties"]["files"]

    assert files_schema["type"] == "array"
    assert files_schema["items"]["type"] == "string"
    if "format" in files_schema["items"]:
        assert files_schema["items"]["format"] == "binary"


def test_txt_upload_indexes_chunks(client: TestClient, fake_indexer: FakeIndexer) -> None:
    response = client.post(
        "/documents/upload",
        files=[
            (
                "files",
                ("notes.txt", b"alpha beta gamma delta epsilon zeta eta theta", "text/plain"),
            )
        ],
    )

    body = response.json()
    assert response.status_code == 201
    assert body["status"] == "indexed"
    assert body["documents"][0]["source_name"] == "notes.txt"
    assert body["documents"][0]["chunks_indexed"] == len(fake_indexer.indexed_chunks)
    assert fake_indexer.indexed_chunks


def test_pdf_upload_indexes_chunks(
    client: TestClient,
    fake_indexer: FakeIndexer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.ingestion.pipeline.load_document_text",
        lambda filename, content: "pdf text alpha beta gamma delta epsilon",
    )

    response = client.post(
        "/documents/upload",
        files=[("files", ("paper.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf"))],
    )

    body = response.json()
    assert response.status_code == 201
    assert body["status"] == "indexed"
    assert body["documents"][0]["source_name"] == "paper.pdf"
    assert fake_indexer.indexed_chunks


def test_invalid_upload_returns_structured_error(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files=[("files", ("image.png", b"not a supported document", "image/png"))],
    )

    body = response.json()
    assert response.status_code == 400
    assert body["detail"]["status"] == "failed"
    assert body["detail"]["errors"][0]["error_code"] == "invalid_document"


def test_multiple_files_upload_indexes_all(client: TestClient, fake_indexer: FakeIndexer) -> None:
    response = client.post(
        "/documents/upload",
        files=[
            ("files", ("one.txt", b"one two three four five six seven", "text/plain")),
            ("files", ("two.md", b"# Two\n\nalpha beta gamma delta", "text/markdown")),
        ],
    )

    body = response.json()
    assert response.status_code == 201
    assert body["status"] == "indexed"
    assert len(body["documents"]) == 2
    assert len(fake_indexer.indexed_chunks) >= 2
