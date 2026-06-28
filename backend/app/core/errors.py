from fastapi import HTTPException, status


class AppError(Exception):
    """Base application error for expected operational failures."""


class ConfigurationError(AppError):
    """Raised when required runtime configuration is missing or invalid."""


class ExternalToolError(AppError):
    """Raised when an external tool call fails in a controlled way."""


class DocumentParsingError(AppError):
    """Raised when an uploaded document cannot be parsed into readable text."""


class EmbeddingError(ExternalToolError):
    """Raised when document embedding generation fails."""


class QdrantError(ExternalToolError):
    """Raised when Qdrant collection or indexing operations fail."""


def service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
