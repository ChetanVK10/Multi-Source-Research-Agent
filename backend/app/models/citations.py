from pydantic import BaseModel, Field


class Citation(BaseModel):
    citation_id: str = Field(..., description="Stable citation identifier shown in the final answer.")
    source_id: str = Field(..., description="Identifier of the source backing this citation.")
    title: str | None = Field(default=None, description="Human-readable source title.")
    url: str | None = Field(default=None, description="External URL when available.")
    snippet: str | None = Field(default=None, description="Short cited excerpt or summary.")
