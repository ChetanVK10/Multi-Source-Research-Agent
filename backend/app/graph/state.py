import operator
from typing import Annotated, Literal, NotRequired, TypedDict

from app.models.citations import Citation
from app.models.evidence import Evidence

SourceType = Literal["documents", "web", "sql"]
ResearchStatus = Literal["created", "planned", "retrieving", "reranking", "synthesizing", "completed", "failed"]


class PlannerDecision(TypedDict):
    required_sources: list[SourceType]
    reasoning: str
    confidence: float


class GraphError(TypedDict):
    node: str
    message: str
    recoverable: bool


class ResearchGraphState(TypedDict):
    query_id: str
    user_query: str
    top_k: NotRequired[int]
    status: ResearchStatus
    planner_decision: NotRequired[PlannerDecision]
    routed_sources: NotRequired[list[SourceType]]
    document_evidence: NotRequired[list[Evidence]]
    web_evidence: NotRequired[list[Evidence]]
    sql_evidence: NotRequired[list[Evidence]]
    merged_evidence: NotRequired[list[Evidence]]
    reranked_evidence: NotRequired[list[Evidence]]
    final_answer: NotRequired[str]
    citations: NotRequired[list[Citation]]
    errors: NotRequired[Annotated[list[GraphError], operator.add]]
    selected_provider: NotRequired[str]
    selected_model: NotRequired[str]
    conversation_id: NotRequired[str]
    history_messages: NotRequired[list[dict]]
