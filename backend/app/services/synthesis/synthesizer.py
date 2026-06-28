import re

from app.core.config import Settings
from app.models.citations import Citation
from app.models.evidence import Evidence
from app.models.synthesis import SynthesisResult
from app.services.llm import LLMClient
from app.services.llm.prompts import build_synthesis_prompt
from app.services.synthesis.citations import build_citations


class GroundedSynthesizer:
    def __init__(self, *, settings: Settings, llm_client: LLMClient) -> None:
        self.settings = settings
        self.llm_client = llm_client

    async def synthesize(
        self, *, question: str, evidence: list[Evidence], history: list[dict] | None = None
    ) -> SynthesisResult:
        citations = build_citations(evidence)
        if not evidence:
            return _insufficient_evidence_result()

        context = _format_context(evidence, citations, self.settings.synthesis_max_context_chars)
        answer = await self.llm_client.ainvoke_text(
            build_synthesis_prompt(question=question, context=context, history=history)
        )
        if self.settings.synthesis_require_citations:
            answer = _enforce_grounding(answer=answer, citations=citations)
        return SynthesisResult(answer=answer, citations=_used_citations(answer, citations))


class ExtractiveFallbackSynthesizer:
    def synthesize(self, *, evidence: list[Evidence]) -> SynthesisResult:
        citations = build_citations(evidence)
        if not evidence:
            return _insufficient_evidence_result()

        lines: list[str] = []
        for citation, item in zip(citations[:4], evidence[:4], strict=False):
            lines.append(f"- {_compact(item.content)} [{citation.citation_id}]")

        return SynthesisResult(
            answer=(
                "I found relevant evidence, but model-based synthesis is unavailable. "
                "Here are the strongest grounded excerpts:\n" + "\n".join(lines)
            ),
            citations=citations[:4],
        )


def _format_context(evidence: list[Evidence], citations: list[Citation], max_chars: int) -> str:
    blocks: list[str] = []
    used_chars = 0
    for citation, item in zip(citations, evidence, strict=True):
        block = (
            f"[{citation.citation_id}]\n"
            f"Source: {item.source}\n"
            f"Title: {item.title or 'Untitled'}\n"
            f"URL: {item.url or 'N/A'}\n"
            f"Content: {item.content}\n"
        )
        if used_chars + len(block) > max_chars:
            break
        blocks.append(block)
        used_chars += len(block)
    return "\n".join(blocks)


def _enforce_grounding(*, answer: str, citations: list[Citation]) -> str:
    if not answer:
        return "The available evidence was not sufficient to generate a grounded answer."

    valid_ids = {citation.citation_id for citation in citations}
    cited_ids = set(re.findall(r"\[(C\d+)\]", answer))
    invalid_ids = cited_ids.difference(valid_ids)
    for invalid_id in invalid_ids:
        answer = answer.replace(f"[{invalid_id}]", "")

    if valid_ids and not re.search(r"\[C\d+\]", answer):
        answer = f"{answer.rstrip()} [{citations[0].citation_id}]"

    return answer.strip()


def _used_citations(answer: str, citations: list[Citation]) -> list[Citation]:
    used_ids = set(re.findall(r"\[(C\d+)\]", answer))
    if not used_ids:
        return citations[:1]
    return [citation for citation in citations if citation.citation_id in used_ids]


def _insufficient_evidence_result() -> SynthesisResult:
    return SynthesisResult(
        answer=(
            "I do not have enough retrieved evidence to answer this question reliably. "
            "Try uploading relevant documents, enabling web search, or configuring SQL retrieval."
        ),
        citations=[],
    )


def _compact(content: str, max_chars: int = 320) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3].rstrip()}..."
