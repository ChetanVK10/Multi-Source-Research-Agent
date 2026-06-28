"""SQLite-backed conversation service — drop-in replacement for ConversationMemoryService.

Public interface is identical to the old in-memory service so all callers
(synthesizer_node, planner_node, chats router) work without modification.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.db.database import get_session
from app.db.models import ConversationModel, MessageModel
from app.models.citations import Citation
from app.models.evidence import Evidence


# ── Pydantic DTOs (same shapes as the old ConversationMemoryService) ──────────


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Assistant metadata — fully persisted and restored on reload
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


# ── Helpers ───────────────────────────────────────────────────────────────────


def _row_to_message(row: MessageModel) -> Message:
    """Convert a MessageModel ORM row to a Pydantic Message DTO."""
    raw_citations = row.get_citations()
    raw_evidence = row.get_evidence()

    return Message(
        role=row.role,  # type: ignore[arg-type]
        content=row.content,
        timestamp=row.timestamp.replace(tzinfo=UTC) if row.timestamp.tzinfo is None else row.timestamp,
        citations=[Citation(**c) for c in raw_citations],
        evidence=[Evidence(**e) for e in raw_evidence],
        provider=row.provider,
        model=row.model,
    )


def _row_to_conversation(row: ConversationModel) -> Conversation:
    """Convert a ConversationModel ORM row (with messages) to a Pydantic Conversation DTO."""
    return Conversation(
        conversation_id=row.conversation_id,
        title=row.title,
        created_at=row.created_at.replace(tzinfo=UTC) if row.created_at.tzinfo is None else row.created_at,
        updated_at=row.updated_at.replace(tzinfo=UTC) if row.updated_at.tzinfo is None else row.updated_at,
        messages=[_row_to_message(m) for m in row.messages],
    )


# ── Service ───────────────────────────────────────────────────────────────────

_MESSAGE_LIMIT = 15


class SQLConversationService:
    """Persistent conversation store backed by SQLite via SQLAlchemy."""

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        with get_session() as db:
            row = db.get(ConversationModel, conversation_id)
            if row is None:
                return None
            return _row_to_conversation(row)

    def get_or_create_conversation(self, conversation_id: str) -> Conversation:
        # Validate / normalise UUID
        try:
            uuid.UUID(conversation_id)
        except ValueError:
            conversation_id = str(uuid.uuid4())

        with get_session() as db:
            row = db.get(ConversationModel, conversation_id)
            if row is None:
                row = ConversationModel(
                    conversation_id=conversation_id,
                    title="New Chat",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                db.add(row)
                db.flush()  # populate relationship list before read
            return _row_to_conversation(row)

    def list_conversations(self) -> list[Conversation]:
        with get_session() as db:
            rows = (
                db.query(ConversationModel)
                .order_by(ConversationModel.updated_at.desc())
                .all()
            )
            return [_row_to_conversation(r) for r in rows]

    # ── Write ─────────────────────────────────────────────────────────────────

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
        citations = citations or []
        evidence = evidence or []

        with get_session() as db:
            # Ensure conversation exists
            conv_row = db.get(ConversationModel, conversation_id)
            if conv_row is None:
                conv_row = ConversationModel(
                    conversation_id=conversation_id,
                    title="New Chat",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                db.add(conv_row)
                db.flush()

            now = datetime.now(UTC)

            msg_row = MessageModel(
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=now,
                citations_json=json.dumps([c.model_dump() for c in citations]),
                evidence_json=json.dumps([e.model_dump() for e in evidence]),
                provider=provider,
                model=model,
            )
            db.add(msg_row)
            db.flush()

            # Enforce 15-message limit: delete oldest messages beyond the cap
            message_ids = (
                db.query(MessageModel.id)
                .filter(MessageModel.conversation_id == conversation_id)
                .order_by(MessageModel.id.asc())
                .all()
            )
            if len(message_ids) > _MESSAGE_LIMIT:
                ids_to_delete = [row.id for row in message_ids[: len(message_ids) - _MESSAGE_LIMIT]]
                db.query(MessageModel).filter(MessageModel.id.in_(ids_to_delete)).delete(
                    synchronize_session=False
                )

            # Bump updated_at on the conversation
            conv_row.updated_at = now

        return Message(
            role=role,  # type: ignore[arg-type]
            content=content,
            timestamp=now,
            citations=citations,
            evidence=evidence,
            provider=provider,
            model=model,
        )

    def update_title(self, conversation_id: str, title: str) -> Conversation | None:
        with get_session() as db:
            row = db.get(ConversationModel, conversation_id)
            if row is None:
                return None
            row.title = title
            row.updated_at = datetime.now(UTC)
            db.flush()
            return _row_to_conversation(row)

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_conversation(self, conversation_id: str) -> bool:
        with get_session() as db:
            row = db.get(ConversationModel, conversation_id)
            if row is None:
                return False
            db.delete(row)
            return True

    def delete_all_conversations(self) -> None:
        with get_session() as db:
            db.query(ConversationModel).delete(synchronize_session=False)


# Global singleton — same export name as before
memory_service = SQLConversationService()
