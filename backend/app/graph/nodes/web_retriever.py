from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.services.web.factory import build_web_search_tool
from app.services.web.retriever import WebRetriever

logger = get_logger(__name__)


async def web_retriever_node(state: ResearchGraphState) -> dict[str, Any]:
    settings = get_settings()

    try:
        retriever = WebRetriever(
            settings=settings,
            search_tool=build_web_search_tool(settings),
        )
        evidence = await retriever.search(query=state["user_query"])
        logger.info(
            "Web retriever returned %s results for query_id=%s",
            len(evidence),
            state["query_id"],
        )
        return {"web_evidence": evidence}
    except AppError as exc:
        logger.warning("Web retrieval failed for query_id=%s: %s", state["query_id"], exc)
        return {
            "web_evidence": [],
            "errors": [
                {
                    "node": "web_retriever",
                    "message": str(exc),
                    "recoverable": True,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Unexpected web retrieval failure for query_id=%s", state["query_id"])
        return {
            "web_evidence": [],
            "errors": [
                {
                    "node": "web_retriever",
                    "message": f"Unexpected web retrieval error: {exc}",
                    "recoverable": True,
                }
            ],
        }
