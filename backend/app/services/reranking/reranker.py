import math
from functools import lru_cache

from app.core.config import Settings
from app.core.errors import ExternalToolError
from app.models.evidence import Evidence


class CrossEncoderReranker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = _load_cross_encoder(settings.reranker_model_name)

    def rerank(self, *, query: str, evidence: list[Evidence], top_k: int) -> list[Evidence]:
        if not evidence:
            return []

        pairs = [(query, item.content) for item in evidence]
        try:
            raw_scores = self._model.predict(
                pairs,
                batch_size=self.settings.reranker_batch_size,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise ExternalToolError(f"Cross-encoder reranking failed: {exc}") from exc

        normalized_scores = _normalize_scores([float(score) for score in raw_scores])
        scored = [
            item.model_copy(update={"score": score})
            for item, score in zip(evidence, normalized_scores, strict=True)
        ]
        return sorted(scored, key=lambda item: item.score or 0.0, reverse=True)[:top_k]


class LexicalFallbackReranker:
    def rerank(self, *, query: str, evidence: list[Evidence], top_k: int) -> list[Evidence]:
        query_terms = _terms(query)
        scored = [
            item.model_copy(update={"score": _lexical_score(query_terms, item)})
            for item in evidence
        ]
        return sorted(scored, key=lambda item: item.score or 0.0, reverse=True)[:top_k]


@lru_cache
def _load_cross_encoder(model_name: str) -> object:
    try:
        from sentence_transformers import CrossEncoder

        return CrossEncoder(model_name)
    except Exception as exc:
        raise ExternalToolError(f"Could not load cross-encoder model '{model_name}': {exc}") from exc


def _normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)
    if math.isclose(minimum, maximum):
        sigmoid = 1.0 / (1.0 + math.exp(-scores[0]))
        return [max(0.0, min(1.0, sigmoid)) for _ in scores]

    return [(score - minimum) / (maximum - minimum) for score in scores]


def _terms(text: str) -> set[str]:
    return {term for term in text.lower().split() if len(term) >= 3}


def _lexical_score(query_terms: set[str], evidence: Evidence) -> float:
    if not query_terms:
        return evidence.score or 0.0

    content_terms = _terms(f"{evidence.title or ''} {evidence.content}")
    overlap = len(query_terms.intersection(content_terms)) / len(query_terms)
    prior = evidence.score or 0.0
    return max(0.0, min(1.0, (0.75 * overlap) + (0.25 * prior)))
