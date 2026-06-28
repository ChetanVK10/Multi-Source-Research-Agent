from app.core.config import Settings, get_settings
from app.services.web.search_tool import WebSearchTool
from app.services.web.tavily_tool import TavilySearchTool


def build_web_search_tool(settings: Settings | None = None) -> WebSearchTool:
    resolved_settings = settings or get_settings()

    if resolved_settings.web_search_provider == "tavily":
        return TavilySearchTool(resolved_settings)

    raise ValueError(f"Unsupported web search provider: {resolved_settings.web_search_provider}")
