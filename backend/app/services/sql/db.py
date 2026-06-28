from typing import Any

from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError
from app.models.sql import SQLColumn, SQLTableSchema


class PostgreSQLClient:
    def __init__(self, settings: Settings) -> None:
        if settings.database_url is None:
            raise ConfigurationError("DATABASE_URL is required for SQL retrieval.")

        self.database_url = settings.database_url.get_secret_value()
        if not self.database_url:
            raise ConfigurationError("DATABASE_URL is required for SQL retrieval.")

        self.statement_timeout_ms = settings.sql_statement_timeout_ms

    async def fetch_schema(self, allowed_tables: list[str]) -> list[SQLTableSchema]:
        if not allowed_tables:
            raise ConfigurationError("SQL_ALLOWED_TABLES must include at least one table.")

        rows = await self.fetch(
            """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = ANY($1::text[])
            ORDER BY table_name, ordinal_position
            """,
            [allowed_tables],
        )

        grouped: dict[str, list[SQLColumn]] = {}
        for row in rows:
            grouped.setdefault(row["table_name"], []).append(
                SQLColumn(name=row["column_name"], data_type=row["data_type"])
            )

        return [
            SQLTableSchema(table_name=table_name, columns=columns)
            for table_name, columns in grouped.items()
        ]

    async def fetch(self, sql: str, parameters: list[Any]) -> list[dict[str, Any]]:
        import asyncpg

        try:
            connection = await asyncpg.connect(self.database_url)
            try:
                await connection.execute(f"SET statement_timeout = {self.statement_timeout_ms}")
                records = await connection.fetch(sql, *parameters)
                return [dict(record) for record in records]
            finally:
                await connection.close()
        except asyncpg.PostgresError as exc:
            raise ExternalToolError(f"PostgreSQL query failed: {exc}") from exc
