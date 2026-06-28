from typing import Protocol

from app.models.web import WebSearchResult


class WebSearchTool(Protocol):
    async def search(self, *, query: str, max_results: int) -> list[WebSearchResult]:
        """Run a web search and return normalized results."""
