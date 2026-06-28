from typing import Literal

from pydantic import BaseModel

from app.models.citations import Citation
from app.models.evidence import Evidence


class DependencyHealth(BaseModel):
    status: Literal["ok", "degraded", "unconfigured"]
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    app_version: str
    environment: str
    services: dict[str, DependencyHealth] = {}


class ResearchQueryResponse(BaseModel):
    query_id: str
    status: Literal["accepted", "completed", "failed"]
    answer: str | None
    citations: list[Citation]
    evidence: list[Evidence]
    message: str | None = None
    provider: str | None = None
    model: str | None = None
    conversation_id: str | None = None


class ModelConfigResponse(BaseModel):
    id: str
    name: str


class ProviderConfigResponse(BaseModel):
    id: str
    name: str
    models: list[ModelConfigResponse]
    is_available: bool
