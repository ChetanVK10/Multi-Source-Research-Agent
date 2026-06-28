from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Stable chunk identifier.")
    document_id: str = Field(..., description="Identifier shared by chunks from the same document.")
    text: str = Field(..., min_length=1, description="Chunk text to embed and retrieve.")
    chunk_index: int = Field(..., ge=0)
    title: str | None = None
    source_name: str | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class DocumentIngestionResult(BaseModel):
    document_id: str = Field(..., description="Stable ID assigned to the indexed document.")
    source_name: str = Field(..., description="Original uploaded filename.")
    chunks_indexed: int = Field(..., ge=1, description="Number of chunks embedded and indexed.")


class DocumentUploadResponse(BaseModel):
    status: str = Field(..., description="Batch upload status.")
    documents: list[DocumentIngestionResult] = Field(
        default_factory=list,
        description="Successfully indexed documents.",
    )
    errors: list["DocumentUploadError"] = Field(
        default_factory=list,
        description="Per-file upload failures.",
    )


class DocumentUploadError(BaseModel):
    filename: str = Field(..., description="Uploaded filename that failed processing.")
    error_code: str = Field(..., description="Stable client-readable failure code.")
    message: str = Field(..., description="Human-readable error details.")
