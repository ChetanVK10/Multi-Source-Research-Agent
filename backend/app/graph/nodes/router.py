from typing import Any

from app.core.logging import get_logger
from app.graph.state import ResearchGraphState, SourceType

logger = get_logger(__name__)


def router_node(state: ResearchGraphState) -> dict[str, Any]:
    planner_decision = state.get("planner_decision")
    if planner_decision is None:
        logger.error("Router received query_id=%s without a planner decision", state["query_id"])
        return {
            "status": "failed",
            "errors": [
                *state.get("errors", []),
                {
                    "node": "router",
                    "message": "Planner decision is missing.",
                    "recoverable": False,
                },
            ],
        }

    routed_sources = planner_decision["required_sources"]
    logger.info("Router selected branches for query_id=%s sources=%s", state["query_id"], routed_sources)

    return {"status": "retrieving", "routed_sources": routed_sources}


def route_to_required_sources(state: ResearchGraphState) -> list[SourceType] | str:
    if state["status"] == "failed":
        return "__end__"
    return state.get("routed_sources", [])
