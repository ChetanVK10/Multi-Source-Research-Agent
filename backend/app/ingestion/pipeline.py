from datetime import UTC

from app.core.config import Settings
from app.ingestion.chunking import TextChunker
from app.ingestion.loaders import load_document_text
from app.models.documents import DocumentIngestionResult
from app.services.vectorstore.document_indexer import DocumentIndexer
from app.utils.ids import stable_id


class DocumentIngestionPipeline:
    def __init__(self, settings: Settings, indexer: DocumentIndexer) -> None:
        self.settings = settings
        self.indexer = indexer
        self.chunker = TextChunker(
            chunk_size=settings.document_chunk_size,
            chunk_overlap=settings.document_chunk_overlap,
        )

    async def ingest_file(self, *, filename: str, content: bytes) -> DocumentIngestionResult:
        text = load_document_text(filename, content)
        document_id = stable_id(f"{filename}:{len(content)}:{text[:128]}")
        from datetime import datetime
        chunks = self.chunker.split(
            document_id=document_id,
            text=text,
            source_name=filename,
            title=filename,
            metadata={
                "filename": filename,
                "upload_time": datetime.now(UTC).isoformat(),
            },
        )

        if not chunks:
            raise ValueError(f"No readable text found in {filename}")

        await self.indexer.index_chunks(chunks)
        return DocumentIngestionResult(
            document_id=document_id,
            source_name=filename,
            chunks_indexed=len(chunks),
        )
