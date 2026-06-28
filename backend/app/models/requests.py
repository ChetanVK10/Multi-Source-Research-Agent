from uuid import uuid4

from pydantic import BaseModel, Field


class ResearchQueryRequest(BaseModel):
    query_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Client-supplied or generated request identifier.",
    )
    question: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Research question to answer using routed sources.",
    )
    top_k: int = Field(
        default=8,
        ge=1,
        le=25,
        description="Maximum number of reranked evidence items to keep.",
    )
    include_sources: bool = Field(
        default=True,
        description="Whether to include retrieved evidence in the response.",
    )
    provider: str | None = Field(
        default=None,
        description="LLM provider to use for response synthesis.",
    )
    model: str | None = Field(
        default=None,
        description="LLM model name to use for response synthesis.",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional conversation identifier for multi-turn history.",
    )
