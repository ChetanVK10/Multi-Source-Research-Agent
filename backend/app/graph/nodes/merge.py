from typing import Any

from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.models.evidence import Evidence

logger = get_logger(__name__)


def merge_node(state: ResearchGraphState) -> dict[str, Any]:
    merged = _dedupe_evidence(
        [
            *state.get("document_evidence", []),
            *state.get("web_evidence", []),
            *state.get("sql_evidence", []),
        ]
    )

    logger.info("Merged %s evidence items for query_id=%s", len(merged), state["query_id"])
    return {"merged_evidence": merged, "status": "reranking"}


def _dedupe_evidence(evidence_items: list[Evidence]) -> list[Evidence]:
    seen: set[str] = set()
    deduped: list[Evidence] = []

    for item in evidence_items:
        dedupe_key = item.url or item.evidence_id or item.content[:160]
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        deduped.append(item)

    return deduped
