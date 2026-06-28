from typing import Any

from app.core.logging import get_logger
from app.graph.state import PlannerDecision, ResearchGraphState, SourceType

logger = get_logger(__name__)

DOCUMENT_SIGNALS = {
    "document",
    "documents",
    "uploaded",
    "upload",
    "file",
    "files",
    "pdf",
    "report",
    "reports",
    "policy",
    "contract",
    "memo",
    "deck",
    "internal",
    "knowledge base",
}

WEB_SIGNALS = {
    "latest",
    "current",
    "recent",
    "today",
    "news",
    "market",
    "competitor",
    "competitors",
    "web",
    "internet",
    "external",
    "public",
    "trend",
    "trends",
}

SQL_SIGNALS = {
    "sql",
    "database",
    "table",
    "records",
    "revenue",
    "sales",
    "customer",
    "customers",
    "churn",
    "retention",
    "pipeline",
    "transactions",
    "orders",
    "kpi",
    "metrics",
}


from app.services.memory import memory_service


def planner_node(state: ResearchGraphState) -> dict[str, Any]:
    query = state["user_query"]
    normalized_query = query.lower()

    required_sources: list[SourceType] = []
    matched_reasons: list[str] = []

    if _contains_any(normalized_query, DOCUMENT_SIGNALS):
        required_sources.append("documents")
        matched_reasons.append("the query references uploaded, internal, or document-style evidence")

    if _contains_any(normalized_query, WEB_SIGNALS):
        required_sources.append("web")
        matched_reasons.append("the query asks for current, public, market, or web evidence")

    if _contains_any(normalized_query, SQL_SIGNALS):
        required_sources.append("sql")
        matched_reasons.append("the query appears to require structured business data")

    if not required_sources:
        required_sources = ["documents", "web"]
        matched_reasons.append(
            "no narrow source signal was detected, so document and web evidence are both useful"
        )

    decision = PlannerDecision(
        required_sources=_dedupe_sources(required_sources),
        reasoning="; ".join(matched_reasons),
        confidence=_confidence(required_sources),
    )

    logger.info(
        "Planner selected sources for query_id=%s sources=%s",
        state["query_id"],
        decision["required_sources"],
    )

    conversation_id = state.get("conversation_id")
    history_messages: list[dict[str, Any]] = []
    if conversation_id:
        conversation = memory_service.get_or_create_conversation(conversation_id)
        history_messages = [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
            for m in conversation.messages
        ]

    return {
        "status": "planned",
        "planner_decision": decision,
        "history_messages": history_messages,
    }


def _contains_any(text: str, signals: set[str]) -> bool:
    return any(signal in text for signal in signals)


def _dedupe_sources(sources: list[SourceType]) -> list[SourceType]:
    ordered_sources: list[SourceType] = []
    for source in sources:
        if source not in ordered_sources:
            ordered_sources.append(source)
    return ordered_sources


def _confidence(sources: list[SourceType]) -> float:
    if len(sources) == 1:
        return 0.72
    if len(sources) == 2:
        return 0.82
    return 0.9
