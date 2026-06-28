from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.graph.state import ResearchGraphState
from app.services.llm import get_llm_client
from app.services.synthesis.synthesizer import (
    ExtractiveFallbackSynthesizer,
    GroundedSynthesizer,
)

logger = get_logger(__name__)

from app.services.memory import memory_service


async def synthesizer_node(state: ResearchGraphState) -> dict[str, Any]:
    settings = get_settings()
    evidence = state.get("reranked_evidence", [])
    conversation_id = state.get("conversation_id")

    if not evidence:
        logger.info(
            "No evidence available for synthesis query_id=%s",
            state["query_id"],
        )

        result = ExtractiveFallbackSynthesizer().synthesize(
            evidence=evidence,
        )

        # Save conversation even in fallback case
        if conversation_id:
            memory_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=state["user_query"],
            )

            memory_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.answer,
                citations=result.citations,
                evidence=evidence,
            )

        return {
            "final_answer": result.answer,
            "citations": result.citations,
            "status": "completed",
        }

    try:
        llm_client = get_llm_client(
            provider=state.get("selected_provider"),
            model=state.get("selected_model"),
            settings=settings,
        )

        synthesizer = GroundedSynthesizer(
            settings=settings,
            llm_client=llm_client,
        )

        history = state.get("history_messages")

        result = await synthesizer.synthesize(
            question=state["user_query"],
            evidence=evidence,
            history=history,
        )

        logger.info(
            "Synthesized answer for query_id=%s evidence_count=%s citation_count=%s",
            state["query_id"],
            len(evidence),
            len(result.citations),
        )

        if conversation_id:
            conversation = memory_service.get_or_create_conversation(
                conversation_id
            )

            if conversation.title == "New Chat" or not conversation.title:
                try:
                    title_prompt = (
                        "Generate a short, concise, and clean chat title (3-5 words) "
                        "representing this query. Do not use quotes, markdown formatting, "
                        "or preamble. Just return the title.\n\n"
                        f"Query: {state['user_query']}"
                    )

                    title = await llm_client.ainvoke_text(title_prompt)
                    title = title.strip().strip('"').strip("'").strip()

                    if title:
                        memory_service.update_title(
                            conversation_id,
                            title,
                        )

                except Exception as title_err:
                    logger.warning(
                        "Could not generate automatic chat title: %s",
                        title_err,
                    )

                    fallback_title = (
                        state["user_query"][:30] + "..."
                        if len(state["user_query"]) > 30
                        else state["user_query"]
                    )

                    memory_service.update_title(
                        conversation_id,
                        fallback_title,
                    )

            # Save user message
            memory_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=state["user_query"],
            )

            # Save assistant message with metadata
            memory_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.answer,
                citations=result.citations,
                evidence=evidence,
                provider=llm_client.provider,
                model=llm_client.model,
            )

        return {
            "final_answer": result.answer,
            "citations": result.citations,
            "status": "completed",
            "selected_provider": llm_client.provider,
            "selected_model": llm_client.model,
        }

    except AppError as exc:
        logger.warning(
            "Synthesis failed for query_id=%s, using fallback: %s",
            state["query_id"],
            exc,
        )

        result = ExtractiveFallbackSynthesizer().synthesize(
            evidence=evidence,
        )

        if conversation_id:
            memory_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=state["user_query"],
            )

            memory_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.answer,
                citations=result.citations,
                evidence=evidence,
            )

        return {
            "final_answer": result.answer,
            "citations": result.citations,
            "status": "completed",
            "errors": [
                {
                    "node": "synthesizer",
                    "message": f"Extractive fallback used: {exc}",
                    "recoverable": True,
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Unexpected synthesis failure for query_id=%s",
            state["query_id"],
        )

        result = ExtractiveFallbackSynthesizer().synthesize(
            evidence=evidence,
        )

        if conversation_id:
            memory_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=state["user_query"],
            )

            memory_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.answer,
                citations=result.citations,
                evidence=evidence,
            )

        return {
            "final_answer": result.answer,
            "citations": result.citations,
            "status": "completed",
            "errors": [
                {
                    "node": "synthesizer",
                    "message": f"Unexpected synthesis error, fallback used: {exc}",
                    "recoverable": True,
                }
            ],
        }