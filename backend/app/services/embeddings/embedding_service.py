from functools import lru_cache

from app.core.config import Settings
from app.core.errors import EmbeddingError


@lru_cache
def _load_embedding_model(model_name: str):
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=model_name,
    )


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self._client = _load_embedding_model(settings.embedding_model)

    async def embed_query(self, text: str) -> list[float]:
        try:
            return self._client.embed_query(text)
        except Exception as exc:
            raise EmbeddingError(
                f"Embedding query failed: {exc}"
            ) from exc

    async def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        if not texts:
            return []

        try:
            return self._client.embed_documents(texts)
        except Exception as exc:
            raise EmbeddingError(
                f"Document embedding failed: {exc}"
            ) from exc