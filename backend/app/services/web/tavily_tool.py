from typing import Any

from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError
from app.models.web import WebSearchResult

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class TavilySearchTool:
    def __init__(self, settings: Settings) -> None:
        if settings.web_search_api_key is None:
            raise ConfigurationError("WEB_SEARCH_API_KEY is required for Tavily web search.")

        self.api_key = settings.web_search_api_key.get_secret_value()
        self.timeout_seconds = settings.web_search_timeout_seconds

    async def search(self, *, query: str, max_results: int) -> list[WebSearchResult]:
        import httpx

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(TAVILY_SEARCH_URL, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ExternalToolError("Tavily search timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalToolError(
                f"Tavily search failed with status {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalToolError("Tavily search request failed.") from exc

        body = response.json()
        raw_results = body.get("results", [])
        if not isinstance(raw_results, list):
            raise ExternalToolError("Tavily search returned an invalid response shape.")

        return [_to_web_result(result) for result in raw_results if isinstance(result, dict)]


def _to_web_result(result: dict[str, Any]) -> WebSearchResult:
    return WebSearchResult(
        title=str(result.get("title") or "Untitled web result"),
        url=str(result.get("url") or ""),
        content=str(result.get("content") or ""),
        score=_normalize_score(result.get("score")),
        published_date=_optional_str(result.get("published_date")),
        provider="tavily",
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _normalize_score(value: object) -> float | None:
    if value is None:
        return None
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return None
