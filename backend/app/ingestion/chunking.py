from app.models.documents import DocumentChunk
from app.utils.ids import stable_id


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        *,
        document_id: str,
        text: str,
        source_name: str,
        title: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> list[DocumentChunk]:
        normalized_text = _normalize_text(text)
        if not normalized_text:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_index = 0

        while start < len(normalized_text):
            end = min(start + self.chunk_size, len(normalized_text))
            if end < len(normalized_text):
                boundary = normalized_text.rfind(" ", start, end)
                if boundary > start + int(self.chunk_size * 0.6):
                    end = boundary

            chunk_text = normalized_text[start:end].strip()
            if chunk_text:
                chunk_id = stable_id(f"{document_id}:{chunk_index}:{chunk_text[:64]}")
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        text=chunk_text,
                        chunk_index=chunk_index,
                        title=title,
                        source_name=source_name,
                        metadata=metadata or {},
                    )
                )
                chunk_index += 1

            if end >= len(normalized_text):
                break
            start = max(0, end - self.chunk_overlap)

        return chunks


def _normalize_text(text: str) -> str:
    return " ".join(text.split())
