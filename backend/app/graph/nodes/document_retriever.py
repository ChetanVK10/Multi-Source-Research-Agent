from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.services.vectorstore.factory import build_document_indexer

logger = get_logger(__name__)


async def document_retriever_node(state: ResearchGraphState) -> dict[str, Any]:
    settings = get_settings()

    try:
        indexer = build_document_indexer(settings)
        evidence = await indexer.search(
            query=state["user_query"],
            top_k=settings.document_retrieval_top_k,
        )
        logger.info(
            "Document retriever returned %s chunks for query_id=%s",
            len(evidence),
            state["query_id"],
        )
        return {"document_evidence": evidence}
    except AppError as exc:
        logger.exception("Document retrieval failed for query_id=%s", state["query_id"])
        return {
            "document_evidence": [],
            "errors": [
                *state.get("errors", []),
                {
                    "node": "document_retriever",
                    "message": str(exc),
                    "recoverable": True,
                },
            ],
        }
    except Exception as exc:
        logger.exception("Unexpected document retrieval failure for query_id=%s", state["query_id"])
        return {
            "document_evidence": [],
            "errors": [
                *state.get("errors", []),
                {
                    "node": "document_retriever",
                    "message": f"Unexpected document retrieval error: {exc}",
                    "recoverable": True,
                },
            ],
        }
