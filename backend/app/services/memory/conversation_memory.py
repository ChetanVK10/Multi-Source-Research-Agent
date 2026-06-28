import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.citations import Citation
from app.models.evidence import Evidence


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Assistant metadata
    citations: list[Citation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

    provider: str | None = None
    model: str | None = None


class Conversation(BaseModel):
    conversation_id: str
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    messages: list[Message] = Field(default_factory=list)


class ConversationMemoryService:
    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._store.get(conversation_id)

    def get_or_create_conversation(self, conversation_id: str) -> Conversation:
        # Validate UUID format. If invalid, generate a clean UUID.
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            conversation_id = str(uuid.uuid4())

        if conversation_id not in self._store:
            self._store[conversation_id] = Conversation(
                conversation_id=conversation_id
            )

        return self._store[conversation_id]

    def list_conversations(self) -> list[Conversation]:
        # Sort by most recently updated
        return sorted(
            self._store.values(),
            key=lambda c: c.updated_at,
            reverse=True,
        )

    def add_message(
        self,
        conversation_id: str,
        role: Literal["user", "assistant"],
        content: str,
        citations: list[Citation] | None = None,
        evidence: list[Evidence] | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> Message:
        conversation = self.get_or_create_conversation(conversation_id)

        message = Message(
            role=role,
            content=content,
            citations=citations or [],
            evidence=evidence or [],
            provider=provider,
            model=model,
        )

        conversation.messages.append(message)

        # Keep only the latest 15 messages
        if len(conversation.messages) > 15:
            conversation.messages = conversation.messages[-15:]

        conversation.updated_at = datetime.now(UTC)

        return message

    def update_title(
        self,
        conversation_id: str,
        title: str,
    ) -> Conversation | None:
        conversation = self.get_conversation(conversation_id)

        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.now(UTC)
            return conversation

        return None

    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self._store:
            del self._store[conversation_id]
            return True
        return False

    def delete_all_conversations(self) -> None:
        self._store.clear()


# Global singleton
memory_service = ConversationMemoryService()