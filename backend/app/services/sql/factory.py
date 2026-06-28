from app.core.config import Settings, get_settings
from app.services.sql.db import PostgreSQLClient
from app.services.sql.retriever import SQLRetriever


def build_sql_retriever(settings: Settings | None = None) -> SQLRetriever:
    resolved_settings = settings or get_settings()
    return SQLRetriever(
        settings=resolved_settings,
        client=PostgreSQLClient(resolved_settings),
    )
