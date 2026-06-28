from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.citations import Citation
from app.models.evidence import Evidence
from app.services.memory import memory_service

router = APIRouter()


class ChatSummary(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatMessageDetail(BaseModel):
    role: str
    content: str
    timestamp: datetime

    citations: list[Citation] = []
    evidence: list[Evidence] = []

    provider: str | None = None
    model: str | None = None


class ChatDetail(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageDetail]


class RenameChatRequest(BaseModel):
    title: str


@router.get(
    "",
    response_model=list[ChatSummary],
    summary="List all active chat conversations",
)
async def list_chats() -> list[ChatSummary]:
    conversations = memory_service.list_conversations()

    return [
        ChatSummary(
            conversation_id=c.conversation_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages),
        )
        for c in conversations
    ]


@router.get(
    "/{conversation_id}",
    response_model=ChatDetail,
    summary="Get full history of a chat conversation",
)
async def get_chat(conversation_id: str) -> ChatDetail:
    conversation = memory_service.get_conversation(conversation_id)

    if not conversation:
        conversation = memory_service.get_or_create_conversation(
            conversation_id
        )

    return ChatDetail(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ChatMessageDetail(
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
                citations=m.citations,
                evidence=m.evidence,
                provider=m.provider,
                model=m.model,
            )
            for m in conversation.messages
        ],
    )


@router.put(
    "/{conversation_id}",
    response_model=ChatSummary,
    summary="Rename a chat conversation title",
)
async def rename_chat(
    conversation_id: str,
    payload: RenameChatRequest,
) -> ChatSummary:
    conversation = memory_service.update_title(
        conversation_id,
        payload.title,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found.",
        )

    return ChatSummary(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=len(conversation.messages),
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat conversation",
)
async def delete_chat(conversation_id: str) -> None:
    memory_service.delete_conversation(conversation_id)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all chat conversations",
)
async def delete_all_chats() -> None:
    memory_service.delete_all_conversations()