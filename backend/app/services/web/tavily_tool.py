from typing import Any

from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError
from app.models.web import WebSearchResult

TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Maximum number of retries on transient network errors
_MAX_RETRIES = 2


class TavilySearchTool:
    def __init__(self, settings: Settings) -> None:
        if settings.web_search_api_key is None:
            raise ConfigurationError("WEB_SEARCH_API_KEY is required for Tavily web search.")

        api_key = settings.web_search_api_key.get_secret_value().strip()
        if not api_key:
            raise ConfigurationError("WEB_SEARCH_API_KEY is empty; cannot initialise Tavily client.")

        self.api_key = api_key
        self.timeout_seconds = settings.web_search_timeout_seconds

    async def search(self, *, query: str, max_results: int) -> list[WebSearchResult]:
        import httpx

        # Tavily REST API v1 authenticates via Bearer token in the Authorization header.
        # Passing api_key inside the JSON body is the old/deprecated method and will
        # return 401 or silently fail on the current API version.
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 2):  # 1 initial + _MAX_RETRIES retries
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout_seconds, connect=10.0)
                ) as client:
                    response = await client.post(
                        TAVILY_SEARCH_URL,
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()

                body = response.json()
                raw_results = body.get("results", [])
                if not isinstance(raw_results, list):
                    raise ExternalToolError("Tavily search returned an invalid response shape.")

                return [_to_web_result(result) for result in raw_results if isinstance(result, dict)]

            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt <= _MAX_RETRIES:
                    continue  # retry on timeout
                raise ExternalToolError(
                    f"Tavily search timed out after {attempt} attempt(s)."
                ) from exc
            except httpx.HTTPStatusError as exc:
                # 4xx errors are not transient – do not retry
                raise ExternalToolError(
                    f"Tavily search failed with HTTP {exc.response.status_code}: "
                    f"{exc.response.text[:200]}"
                ) from exc
            except ExternalToolError:
                raise
            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt <= _MAX_RETRIES:
                    continue  # retry on transient network errors
                raise ExternalToolError("Tavily search request failed.") from exc

        # Should never reach here, but keeps the type checker happy
        raise ExternalToolError("Tavily search failed after all retry attempts.") from last_exc


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
