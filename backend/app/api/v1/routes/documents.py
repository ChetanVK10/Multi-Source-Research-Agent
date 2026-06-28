from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.deps import SettingsDep
from app.core.errors import AppError, DocumentParsingError, EmbeddingError, QdrantError
from app.core.logging import get_logger
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.models.documents import DocumentUploadError, DocumentUploadResponse
from app.services.vectorstore.factory import build_document_indexer

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and index documents",
    description=(
        "Accepts one or more .txt, .md, or .pdf files as multipart/form-data, "
        "parses them, chunks text, embeds chunks, and stores them in Qdrant."
    ),
)
async def upload_documents(
    settings: SettingsDep,
    files: Annotated[
        list[UploadFile],
        File(
            ...,
            description="One or more document files to index.",
            media_type="multipart/form-data",
        ),
    ],
) -> DocumentUploadResponse:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    logger.info("Received document upload request with %s file(s)", len(files))
    try:
        pipeline = DocumentIngestionPipeline(
            settings=settings,
            indexer=build_document_indexer(settings),
        )
    except AppError as exc:
        logger.warning("Document upload pipeline setup failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "document_indexer_unavailable",
                "message": str(exc),
            },
        ) from exc

    results = []
    errors: list[DocumentUploadError] = []
    for file in files:
        filename = file.filename or "document"
        try:
            logger.info(
                "Reading uploaded document filename=%s content_type=%s",
                filename,
                file.content_type,
            )
            content = await file.read()
            result = await pipeline.ingest_file(filename=filename, content=content)
            results.append(result)
            logger.info(
                "Indexed uploaded document filename=%s document_id=%s chunks=%s",
                filename,
                result.document_id,
                result.chunks_indexed,
            )
        except ValueError as exc:
            logger.warning("Document validation failed filename=%s: %s", filename, exc)
            errors.append(_upload_error(filename, "invalid_document", str(exc)))
        except DocumentParsingError as exc:
            logger.warning("Document parsing failed filename=%s: %s", filename, exc)
            errors.append(_upload_error(filename, "document_parsing_failed", str(exc)))
        except EmbeddingError as exc:
            logger.warning("Document embedding failed filename=%s: %s", filename, exc)
            errors.append(_upload_error(filename, "embedding_failed", str(exc)))
        except QdrantError as exc:
            logger.warning("Qdrant indexing failed filename=%s: %s", filename, exc)
            errors.append(_upload_error(filename, "qdrant_failed", str(exc)))
        except AppError as exc:
            logger.warning("Document upload failed filename=%s: %s", filename, exc)
            errors.append(_upload_error(filename, "document_upload_failed", str(exc)))
        except Exception as exc:
            logger.exception("Unexpected document upload failure filename=%s", filename)
            errors.append(_upload_error(filename, "unexpected_upload_error", str(exc)))

    if not results and errors:
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if any(error.error_code in {"embedding_failed", "qdrant_failed"} for error in errors)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": "failed",
                "documents": [],
                "errors": [error.model_dump() for error in errors],
            },
        )

    return DocumentUploadResponse(
        status="partial" if errors else "indexed",
        documents=results,
        errors=errors,
    )


def _upload_error(filename: str, error_code: str, message: str) -> DocumentUploadError:
    return DocumentUploadError(filename=filename, error_code=error_code, message=message)


from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    upload_time: str
    chunk_count: int


@router.get("", response_model=list[DocumentResponse], summary="List all indexed documents")
async def list_documents(settings: SettingsDep) -> list[DocumentResponse]:
    try:
        indexer = build_document_indexer(settings)
        docs = await indexer.list_documents()
        return [
            DocumentResponse(
                document_id=d["document_id"],
                filename=d["filename"],
                upload_time=d["upload_time"],
                chunk_count=d["chunk_count"],
            )
            for d in docs
        ]
    except Exception as exc:
        logger.exception("Failed to list documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete indexed document")
async def delete_document(document_id: str, settings: SettingsDep) -> None:
    try:
        indexer = build_document_indexer(settings)
        await indexer.delete_document(document_id)
    except Exception as exc:
        logger.exception("Failed to delete document document_id=%s", document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all indexed documents")
async def delete_all_documents(settings: SettingsDep) -> None:
    try:
        indexer = build_document_indexer(settings)
        await indexer.delete_all_documents()
    except Exception as exc:
        logger.exception("Failed to delete all documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
