from app.core.config import Settings
from app.models.evidence import Evidence
from app.models.web import WebSearchResult
from app.services.web.search_tool import WebSearchTool
from app.utils.ids import stable_id


class WebRetriever:
    def __init__(self, *, settings: Settings, search_tool: WebSearchTool) -> None:
        self.settings = settings
        self.search_tool = search_tool

    async def search(self, *, query: str) -> list[Evidence]:
        results = await self.search_tool.search(
            query=query,
            max_results=self.settings.web_search_top_k,
        )
        return [_to_evidence(result) for result in results if result.content and result.url]


def _to_evidence(result: WebSearchResult) -> Evidence:
    return Evidence(
        evidence_id=stable_id(f"web:{result.provider}:{result.url}:{result.content[:80]}"),
        source="web",
        content=result.content,
        title=result.title,
        url=result.url,
        metadata={
            "provider": result.provider,
            "published_date": result.published_date,
        },
        score=result.score,
    )
