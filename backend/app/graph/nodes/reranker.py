from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.services.reranking.reranker import CrossEncoderReranker, LexicalFallbackReranker

logger = get_logger(__name__)


def reranker_node(state: ResearchGraphState) -> dict[str, Any]:
    settings = get_settings()
    evidence = state.get("merged_evidence", [])
    top_k = min(state.get("top_k", settings.reranker_top_k), len(evidence))

    if not evidence:
        logger.info("No evidence available to rerank for query_id=%s", state["query_id"])
        return {"reranked_evidence": [], "status": "reranking"}

    try:
        reranker = CrossEncoderReranker(settings)
        reranked = reranker.rerank(query=state["user_query"], evidence=evidence, top_k=top_k)
        logger.info(
            "Cross-encoder reranked %s/%s evidence items for query_id=%s",
            len(reranked),
            len(evidence),
            state["query_id"],
        )
        return {"reranked_evidence": reranked, "status": "reranking"}
    except AppError as exc:
        if not settings.reranker_fallback_enabled:
            logger.warning("Reranking failed for query_id=%s: %s", state["query_id"], exc)
            return _error_result(state, str(exc))

        logger.warning(
            "Cross-encoder unavailable for query_id=%s, using lexical fallback: %s",
            state["query_id"],
            exc,
        )
        reranked = LexicalFallbackReranker().rerank(
            query=state["user_query"],
            evidence=evidence,
            top_k=top_k,
        )
        return {
            "reranked_evidence": reranked,
            "status": "reranking",
            "errors": [
                {
                    "node": "reranker",
                    "message": f"Cross-encoder fallback used: {exc}",
                    "recoverable": True,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Unexpected reranking failure for query_id=%s", state["query_id"])
        return _error_result(state, f"Unexpected reranking error: {exc}")


def _error_result(state: ResearchGraphState, message: str) -> dict[str, Any]:
    return {
        "reranked_evidence": state.get("merged_evidence", []),
        "status": "reranking",
        "errors": [
            {
                "node": "reranker",
                "message": message,
                "recoverable": True,
            }
        ],
    }
