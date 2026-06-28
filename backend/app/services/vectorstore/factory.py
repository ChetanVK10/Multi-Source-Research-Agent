from app.core.config import Settings, get_settings
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectorstore.document_indexer import DocumentIndexer
from app.services.vectorstore.qdrant_client import get_qdrant_client


def build_document_indexer(settings: Settings | None = None) -> DocumentIndexer:
    resolved_settings = settings or get_settings()
    return DocumentIndexer(
        settings=resolved_settings,
        qdrant_client=get_qdrant_client(resolved_settings),
        embedding_service=EmbeddingService(resolved_settings),
    )
