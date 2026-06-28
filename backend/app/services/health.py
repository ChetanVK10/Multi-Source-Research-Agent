from collections.abc import Awaitable, Callable

from app.core.config import Settings
from app.core.errors import ConfigurationError
from app.core.logging import get_logger
from app.models.responses import DependencyHealth

logger = get_logger(__name__)


async def check_dependencies(settings: Settings) -> dict[str, DependencyHealth]:
    checks: dict[str, Callable[[Settings], Awaitable[DependencyHealth]]] = {
        "gemini": check_gemini,
        "groq": check_groq,
        "tavily": check_tavily,
        "postgresql": check_postgresql,
        "qdrant": check_qdrant,
        "embedding_model": check_embedding_model,
    }

    results: dict[str, DependencyHealth] = {}
    for name, check in checks.items():
        results[name] = await check(settings)
    return results


async def validate_startup_dependencies(settings: Settings) -> dict[str, DependencyHealth]:
    results = await check_dependencies(settings)
    for name, result in results.items():
        log = logger.info if result.status == "ok" else logger.warning
        log("Startup dependency validation %s=%s message=%s", name, result.status, result.message)
    return results


async def check_gemini(settings: Settings) -> DependencyHealth:
    # Skip Gemini validation unless Gemini is the primary provider.
    if settings.default_provider != "gemini":
        return _unconfigured("Gemini is not the default provider; skipping validation.")
    if settings.gemini_api_key is None or len(settings.gemini_api_key.get_secret_value().strip()) == 0:
        return _unconfigured("GEMINI_API_KEY is not configured.")

    try:
        from app.services.llm import get_llm_client

        client = get_llm_client("gemini", settings.gemini_model, settings)
        await client.ainvoke_text("Return exactly: ok")
        return _ok("Gemini chat model responded.")
    except Exception as exc:
        return _degraded(f"Gemini validation failed: {exc}")


async def check_groq(settings: Settings) -> DependencyHealth:
    if settings.groq_api_key is None or len(settings.groq_api_key.get_secret_value().strip()) == 0:
        return _unconfigured("GROQ_API_KEY is not configured.")

    try:
        from app.services.llm import get_llm_client

        client = get_llm_client("groq", settings.default_model, settings)
        await client.ainvoke_text("Return exactly: ok")
        return _ok("Groq chat model responded.")
    except Exception as exc:
        return _degraded(f"Groq validation failed: {exc}")


async def check_embedding_model(settings: Settings) -> DependencyHealth:
    # Embedding service uses HuggingFace embeddings and does not depend on Gemini API key.
    try:
        from app.services.embeddings.embedding_service import EmbeddingService

        vector = await EmbeddingService(settings).embed_query("health check")
        if not vector:
            return _degraded("Embedding model returned an empty vector.")
    except Exception as exc:
        return _degraded(f"Embedding validation failed: {exc}")
    return _ok("Embedding model is ready.")


async def check_tavily(settings: Settings) -> DependencyHealth:
    if settings.web_search_api_key is None:
        return _unconfigured("WEB_SEARCH_API_KEY is not configured.")

    try:
        from app.services.web.tavily_tool import TavilySearchTool

        await TavilySearchTool(settings).search(query="health check", max_results=1)
        return _ok("Tavily search responded.")
    except Exception as exc:
        return _degraded(f"Tavily validation failed: {exc}")


async def check_postgresql(settings: Settings) -> DependencyHealth:
    if settings.database_url is None:
        return _unconfigured("DATABASE_URL is not configured.")

    try:
        from app.services.sql.db import PostgreSQLClient

        await PostgreSQLClient(settings).fetch("SELECT 1 AS ok", [])
        return _ok("PostgreSQL responded.")
    except Exception as exc:
        return _degraded(f"PostgreSQL validation failed: {exc}")


async def check_qdrant(settings: Settings) -> DependencyHealth:
    if settings.qdrant_url is None:
        return _unconfigured("QDRANT_URL is not configured.")

    try:
        from app.services.vectorstore.qdrant_client import get_qdrant_client

        client = get_qdrant_client(settings)
        await client.collection_exists(settings.qdrant_collection_name)
        return _ok("Qdrant responded.")
    except ConfigurationError as exc:
        return _unconfigured(str(exc))
    except Exception as exc:
        return _degraded(f"Qdrant validation failed: {exc}")


def _ok(message: str) -> DependencyHealth:
    return DependencyHealth(status="ok", message=message)


def _degraded(message: str) -> DependencyHealth:
    return DependencyHealth(status="degraded", message=message)


def _unconfigured(message: str) -> DependencyHealth:
    return DependencyHealth(status="unconfigured", message=message)
