from app.models.citations import Citation
from app.models.evidence import Evidence


def build_citations(evidence: list[Evidence]) -> list[Citation]:
    citations: list[Citation] = []
    for index, item in enumerate(evidence, start=1):
        citations.append(
            Citation(
                citation_id=f"C{index}",
                source_id=item.evidence_id,
                title=item.title,
                url=item.url,
                snippet=_snippet(item.content),
            )
        )
    return citations


def _snippet(content: str, max_chars: int = 280) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3].rstrip()}..."
