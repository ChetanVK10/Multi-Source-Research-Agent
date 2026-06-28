from functools import lru_cache
from typing import Any

from app.core.config import Settings, get_settings
from app.core.errors import ConfigurationError, QdrantError


def get_qdrant_client(settings: Settings | None = None) -> Any:
    resolved_settings = settings or get_settings()
    if resolved_settings.qdrant_url is None:
        raise ConfigurationError("QDRANT_URL is required for document retrieval.")

    from qdrant_client import AsyncQdrantClient

    return AsyncQdrantClient(
        url=str(resolved_settings.qdrant_url),
        api_key=(
            resolved_settings.qdrant_api_key.get_secret_value()
            if resolved_settings.qdrant_api_key
            else None
        ),
    )


@lru_cache
def qdrant_distance(metric: str) -> Any:
    from qdrant_client.http.models import Distance

    return {
        "Cosine": Distance.COSINE,
        "Dot": Distance.DOT,
        "Euclid": Distance.EUCLID,
    }[metric]


async def ensure_qdrant_collection(
    *,
    client: Any,
    settings: Settings,
) -> None:
    from qdrant_client.http.models import VectorParams

    collection_name = settings.qdrant_collection_name
    try:
        exists = await client.collection_exists(collection_name)
    except Exception as exc:
        raise QdrantError(f"Could not connect to Qdrant collection '{collection_name}'.") from exc

    if exists:
        return

    try:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.qdrant_vector_size,
                distance=qdrant_distance(settings.qdrant_distance_metric),
            ),
        )
    except Exception as exc:
        raise QdrantError(f"Could not create Qdrant collection '{collection_name}'.") from exc
