from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    published_date: str | None = None
    provider: str
