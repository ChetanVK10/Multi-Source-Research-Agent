import re

from app.core.config import Settings
from app.core.errors import ExternalToolError
from app.models.sql import GeneratedSQLQuery, ValidatedSQLQuery

BLOCKED_KEYWORDS = {
    "alter",
    "analyze",
    "call",
    "copy",
    "create",
    "delete",
    "drop",
    "execute",
    "grant",
    "insert",
    "merge",
    "refresh",
    "reindex",
    "revoke",
    "truncate",
    "update",
    "vacuum",
}


class SQLValidator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, generated_query: GeneratedSQLQuery) -> ValidatedSQLQuery:
        sql = generated_query.sql.strip()
        normalized = sql.lower()

        if not normalized.startswith("select "):
            raise ExternalToolError("Only SELECT statements are allowed for SQL retrieval.")

        if ";" in sql.rstrip(";"):
            raise ExternalToolError("Only a single SQL statement is allowed.")

        tokens = set(re.findall(r"[a-z_]+", normalized))
        blocked = tokens.intersection(BLOCKED_KEYWORDS)
        if blocked:
            raise ExternalToolError(f"Blocked SQL keyword detected: {sorted(blocked)[0]}.")

        table_names = self._extract_table_names(sql)
        if not table_names:
            raise ExternalToolError("SQL validation could not identify a table name.")

        allowed_tables = set(self.settings.sql_allowed_tables)
        disallowed = table_names.difference(allowed_tables)
        if disallowed:
            raise ExternalToolError(f"SQL references non-allowlisted table: {sorted(disallowed)[0]}.")

        if " limit " not in f" {normalized} " and "count(" not in normalized and "sum(" not in normalized and "avg(" not in normalized:
            sql = f"{sql.rstrip(';')} LIMIT {self.settings.sql_result_limit}"

        return ValidatedSQLQuery(
            sql=sql.rstrip(";"),
            parameters=generated_query.parameters,
            table_name=generated_query.table_name,
        )

    def _extract_table_names(self, sql: str) -> set[str]:
        matches = re.findall(r'\bfrom\s+"?([a-zA-Z_][a-zA-Z0-9_]*)"?', sql, flags=re.IGNORECASE)
        matches.extend(
            re.findall(r'\bjoin\s+"?([a-zA-Z_][a-zA-Z0-9_]*)"?', sql, flags=re.IGNORECASE)
        )
        return set(matches)
