from typing import Literal

from pydantic import BaseModel, Field

EvidenceSource = Literal["documents", "web", "sql"]


class Evidence(BaseModel):
    evidence_id: str = Field(..., description="Stable evidence identifier.")
    source: EvidenceSource = Field(..., description="Retrieval source that produced this evidence.")
    content: str = Field(..., description="Evidence text used by downstream graph nodes.")
    title: str | None = Field(default=None, description="Source title or record label.")
    url: str | None = Field(default=None, description="URL for web evidence.")
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
