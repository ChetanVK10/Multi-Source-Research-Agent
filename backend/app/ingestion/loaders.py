from pathlib import Path

from app.core.errors import DocumentParsingError

SUPPORTED_EXTENSIONS = {".md", ".pdf", ".txt"}


def load_document_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported document type '{extension}'. Supported types: {supported}")

    if not content or not content.strip():
        raise ValueError(f"Uploaded file '{filename}' is empty.")

    if extension == ".pdf":
        return _load_pdf_text(content)

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentParsingError(f"Could not decode '{filename}' as UTF-8 text.") from exc

    if not text.strip():
        raise ValueError(f"No readable text found in {filename}")
    return text


def _load_pdf_text(content: bytes) -> str:
    from io import BytesIO

    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise DocumentParsingError("Could not parse uploaded PDF document.") from exc

    text = "\n\n".join(page for page in pages if page.strip())
    if not text.strip():
        raise ValueError("No readable text found in uploaded PDF.")
    return text
