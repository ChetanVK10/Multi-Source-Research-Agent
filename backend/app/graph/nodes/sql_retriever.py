from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.services.sql.factory import build_sql_retriever

logger = get_logger(__name__)


async def sql_retriever_node(state: ResearchGraphState) -> dict[str, Any]:
    settings = get_settings()

    try:
        retriever = build_sql_retriever(settings)
        evidence = await retriever.search(question=state["user_query"])
        logger.info(
            "SQL retriever returned %s rows for query_id=%s",
            len(evidence),
            state["query_id"],
        )
        return {"sql_evidence": evidence}
    except AppError as exc:
        logger.warning("SQL retrieval failed for query_id=%s: %s", state["query_id"], exc)
        return {
            "sql_evidence": [],
            "errors": [
                {
                    "node": "sql_retriever",
                    "message": str(exc),
                    "recoverable": True,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Unexpected SQL retrieval failure for query_id=%s", state["query_id"])
        return {
            "sql_evidence": [],
            "errors": [
                {
                    "node": "sql_retriever",
                    "message": f"Unexpected SQL retrieval error: {exc}",
                    "recoverable": True,
                }
            ],
        }
