from typing import Any

from app.core.config import Settings
from app.core.errors import QdrantError
from app.core.logging import get_logger
from app.models.documents import DocumentChunk
from app.models.evidence import Evidence
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectorstore.qdrant_client import ensure_qdrant_collection

logger = get_logger(__name__)


class DocumentIndexer:
    def __init__(
        self,
        *,
        settings: Settings,
        qdrant_client: Any,
        embedding_service: EmbeddingService,
    ) -> None:
        self.settings = settings
        self.qdrant_client = qdrant_client
        self.embedding_service = embedding_service

    async def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        await ensure_qdrant_collection(
            client=self.qdrant_client,
            settings=self.settings,
        )

        logger.info("Embedding %s document chunks", len(chunks))

        vectors = await self.embedding_service.embed_documents(
            [chunk.text for chunk in chunks]
        )

        from qdrant_client.http.models import PointStruct

        points = [
            PointStruct(
                id=chunk.chunk_id,
                vector=vector,
                payload={
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.text,
                    "title": chunk.title,
                    "source_name": chunk.source_name,
                    **chunk.metadata,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

        try:
            await self.qdrant_client.upsert(
                collection_name=self.settings.qdrant_collection_name,
                points=points,
            )
        except Exception as exc:
            raise QdrantError(
                f"Could not store document chunks in Qdrant collection "
                f"'{self.settings.qdrant_collection_name}'."
            ) from exc

        logger.info("Stored %s document chunks in Qdrant", len(points))

    async def search(self, *, query: str, top_k: int) -> list[Evidence]:
        await ensure_qdrant_collection(
            client=self.qdrant_client,
            settings=self.settings,
        )

        logger.info("Embedding retrieval query for document search")

        query_vector = await self.embedding_service.embed_query(query)

        try:
            results = await self.qdrant_client.query_points(
                collection_name=self.settings.qdrant_collection_name,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )

            points = results.points

        except Exception as exc:
            raise QdrantError(
                f"Could not search Qdrant collection "
                f"'{self.settings.qdrant_collection_name}'."
            ) from exc

        evidence: list[Evidence] = []

        for point in points:
            payload = point.payload or {}

            content = str(payload.get("content") or "")

            if not content:
                continue

            evidence.append(
                Evidence(
                    evidence_id=str(payload.get("chunk_id") or point.id),
                    source="documents",
                    content=content,
                    title=_optional_str(
                        payload.get("title") or payload.get("source_name")
                    ),
                    metadata={
                        "document_id": payload.get("document_id"),
                        "chunk_index": payload.get("chunk_index"),
                        "source_name": payload.get("source_name"),
                    },
                    score=_normalize_score(point.score),
                )
            )

        logger.info("Retrieved %d document chunks", len(evidence))

        return evidence

    async def list_documents(self) -> list[dict[str, Any]]:
        collection_name = self.settings.qdrant_collection_name
        try:
            exists = await self.qdrant_client.collection_exists(collection_name)
            if not exists:
                return []
        except Exception:
            return []

        points = []
        offset = None
        while True:
            try:
                res, next_offset = await self.qdrant_client.scroll(
                    collection_name=collection_name,
                    limit=1000,
                    with_payload=True,
                    with_vectors=False,
                    offset=offset,
                )
                points.extend(res)
                if not next_offset:
                    break
                offset = next_offset
            except Exception as exc:
                logger.error("Error scrolling Qdrant points: %s", exc)
                break

        docs_map = {}
        for point in points:
            payload = point.payload or {}
            doc_id = payload.get("document_id")
            if not doc_id:
                continue
            if doc_id not in docs_map:
                filename = (
                    payload.get("filename")
                    or payload.get("source_name")
                    or payload.get("title")
                    or "Unknown Document"
                )
                upload_time = payload.get("upload_time") or "Unknown"
                docs_map[doc_id] = {
                    "document_id": doc_id,
                    "filename": filename,
                    "upload_time": upload_time,
                    "chunk_count": 0,
                }
            docs_map[doc_id]["chunk_count"] += 1

        return list(docs_map.values())

    async def delete_document(self, document_id: str) -> None:
        collection_name = self.settings.qdrant_collection_name
        try:
            exists = await self.qdrant_client.collection_exists(collection_name)
            if not exists:
                return
        except Exception:
            return

        from qdrant_client.http.models import FieldCondition, Filter, MatchValue

        try:
            await self.qdrant_client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                ),
            )
            logger.info("Deleted document %s from Qdrant", document_id)
        except Exception as exc:
            raise QdrantError(
                f"Could not delete document '{document_id}' from collection '{collection_name}'."
            ) from exc

    async def delete_all_documents(self) -> None:
        collection_name = self.settings.qdrant_collection_name
        try:
            exists = await self.qdrant_client.collection_exists(collection_name)
            if not exists:
                return
            await self.qdrant_client.delete_collection(collection_name)
            logger.info("Deleted collection %s from Qdrant", collection_name)
        except Exception as exc:
            raise QdrantError(
                f"Could not delete collection '{collection_name}' from Qdrant."
            ) from exc


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _normalize_score(score: float | None) -> float | None:
    if score is None:
        return None
    return max(0.0, min(1.0, float(score)))