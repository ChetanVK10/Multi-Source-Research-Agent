from typing import Any

from app.core.config import Settings
from app.models.evidence import Evidence
from app.services.sql.db import PostgreSQLClient
from app.services.sql.query_generator import SQLQueryGenerator
from app.services.sql.validator import SQLValidator
from app.utils.ids import stable_id


class SQLRetriever:
    def __init__(self, *, settings: Settings, client: PostgreSQLClient) -> None:
        self.settings = settings
        self.client = client
        self.generator = SQLQueryGenerator(settings)
        self.validator = SQLValidator(settings)

    async def search(self, *, question: str) -> list[Evidence]:
        schemas = await self.client.fetch_schema(self.settings.sql_allowed_tables)
        generated = self.generator.generate(question=question, schemas=schemas)
        validated = self.validator.validate(generated)
        rows = await self.client.fetch(validated.sql, validated.parameters)

        return [
            _row_to_evidence(
                row=row,
                index=index,
                table_name=validated.table_name,
                sql=validated.sql,
                reasoning=generated.reasoning,
            )
            for index, row in enumerate(rows)
        ]


def _row_to_evidence(
    *,
    row: dict[str, Any],
    index: int,
    table_name: str,
    sql: str,
    reasoning: str,
) -> Evidence:
    content = _summarize_row(row)
    return Evidence(
        evidence_id=stable_id(f"sql:{table_name}:{index}:{content}"),
        source="sql",
        content=content,
        title=f"{table_name} row {index + 1}",
        metadata={
            "table_name": table_name,
            "sql": sql,
            "query_generation_reasoning": reasoning,
        },
        score=None,
    )


def _summarize_row(row: dict[str, Any]) -> str:
    if not row:
        return "Empty SQL row."
    parts = [f"{key}: {value}" for key, value in row.items()]
    return "; ".join(parts)
