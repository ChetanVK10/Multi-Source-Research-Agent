from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.logging import get_logger
from app.graph.builder import build_research_graph
from app.models.requests import ResearchQueryRequest
from app.models.responses import ResearchQueryResponse

router = APIRouter()
logger = get_logger(__name__)


import uuid


@router.post(
    "",
    response_model=ResearchQueryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run a grounded research query",
    description=(
        "Plans source usage, retrieves evidence, reranks evidence, "
        "and synthesizes a cited answer."
    ),
)
async def create_research_query(payload: ResearchQueryRequest) -> ResearchQueryResponse:
    settings = get_settings()
    conv_id = payload.conversation_id or str(uuid.uuid4())
    logger.info(
        "Received research query query_id=%s top_k=%s conversation_id=%s",
        payload.query_id,
        payload.top_k,
        conv_id,
    )
    try:
        graph = build_research_graph()
        state = await graph.ainvoke(
            {
                "query_id": payload.query_id,
                "user_query": payload.question,
                "top_k": payload.top_k,
                "status": "created",
                "selected_provider": payload.provider or settings.default_provider,
                "selected_model": payload.model or settings.default_model,
                "conversation_id": conv_id,
            }
        )
    except Exception as exc:
        logger.exception("Research query failed query_id=%s", payload.query_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "research_query_failed",
                "message": str(exc),
            },
        ) from exc

    return ResearchQueryResponse(
        query_id=payload.query_id,
        answer=state.get("final_answer"),
        citations=state.get("citations", []),
        evidence=(
            state.get("reranked_evidence", state.get("merged_evidence", []))
            if payload.include_sources
            else []
        ),
        status=state.get("status", "completed"),
        provider=state.get("selected_provider"),
        model=state.get("selected_model"),
        conversation_id=state.get("conversation_id", conv_id),
        message=(
            "Phase 7 completed grounded synthesis. "
            f"Selected sources: {', '.join(state.get('routed_sources', [])) or 'none'}."
        ),
    )
