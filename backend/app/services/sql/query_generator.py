import re

from app.core.config import Settings
from app.core.errors import ExternalToolError
from app.models.sql import GeneratedSQLQuery, SQLTableSchema

TEXT_TYPES = {"character varying", "text", "character", "varchar"}
NUMERIC_TYPES = {"integer", "bigint", "smallint", "numeric", "double precision", "real", "decimal"}
DATE_TYPES = {"date", "timestamp without time zone", "timestamp with time zone"}
COUNT_SIGNALS = {"count", "number of", "how many", "total records"}
SUM_SIGNALS = {"sum", "total", "revenue", "sales", "amount"}
AVG_SIGNALS = {"average", "avg", "mean"}


class SQLQueryGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, *, question: str, schemas: list[SQLTableSchema]) -> GeneratedSQLQuery:
        if not schemas:
            raise ExternalToolError("No allowed SQL tables were found in the database schema.")

        table = self._choose_table(question, schemas)
        text_columns = [column.name for column in table.columns if column.data_type in TEXT_TYPES]
        numeric_columns = [column.name for column in table.columns if column.data_type in NUMERIC_TYPES]
        date_columns = [column.name for column in table.columns if column.data_type in DATE_TYPES]

        normalized_question = question.lower()
        limit = self.settings.sql_result_limit

        if _contains_any(normalized_question, COUNT_SIGNALS):
            return GeneratedSQLQuery(
                sql=f'SELECT COUNT(*) AS record_count FROM "{table.table_name}"',
                table_name=table.table_name,
                reasoning="The question asks for a count, so a read-only aggregate query was generated.",
            )

        aggregate_column = self._choose_numeric_column(normalized_question, numeric_columns)
        if aggregate_column and _contains_any(normalized_question, AVG_SIGNALS):
            return GeneratedSQLQuery(
                sql=f'SELECT AVG("{aggregate_column}") AS average_{aggregate_column} FROM "{table.table_name}"',
                table_name=table.table_name,
                reasoning="The question asks for an average over a numeric column.",
            )

        if aggregate_column and _contains_any(normalized_question, SUM_SIGNALS):
            return GeneratedSQLQuery(
                sql=f'SELECT SUM("{aggregate_column}") AS total_{aggregate_column} FROM "{table.table_name}"',
                table_name=table.table_name,
                reasoning="The question asks for a total over a numeric column.",
            )

        where_clause, parameters = self._text_search_clause(question, text_columns)
        order_clause = f' ORDER BY "{date_columns[0]}" DESC' if date_columns else ""
        sql = f'SELECT * FROM "{table.table_name}"{where_clause}{order_clause} LIMIT {limit}'
        return GeneratedSQLQuery(
            sql=sql,
            parameters=parameters,
            table_name=table.table_name,
            reasoning="The question asks for relevant records, so a read-only row retrieval query was generated.",
        )

    def _choose_table(self, question: str, schemas: list[SQLTableSchema]) -> SQLTableSchema:
        if self.settings.sql_default_table:
            for schema in schemas:
                if schema.table_name == self.settings.sql_default_table:
                    return schema

        tokens = set(_tokens(question))
        scored = sorted(
            schemas,
            key=lambda schema: len(tokens.intersection(_schema_terms(schema))),
            reverse=True,
        )
        return scored[0]

    def _choose_numeric_column(self, question: str, columns: list[str]) -> str | None:
        if not columns:
            return None

        tokens = set(_tokens(question))
        for column in columns:
            if column.lower() in tokens or tokens.intersection(column.lower().split("_")):
                return column

        preferred = ["revenue", "sales", "amount", "value", "price", "total"]
        for signal in preferred:
            for column in columns:
                if signal in column.lower():
                    return column

        return columns[0]

    def _text_search_clause(self, question: str, text_columns: list[str]) -> tuple[str, list[str]]:
        keywords = [token for token in _tokens(question) if len(token) >= 4][:5]
        if not text_columns or not keywords:
            return "", []

        search_value = f"%{' '.join(keywords)}%"
        conditions = [f'"{column}" ILIKE $1' for column in text_columns[:4]]
        return f" WHERE {' OR '.join(conditions)}", [search_value]


def _contains_any(text: str, signals: set[str]) -> bool:
    return any(signal in text for signal in signals)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower())


def _schema_terms(schema: SQLTableSchema) -> set[str]:
    terms = set(schema.table_name.lower().split("_"))
    for column in schema.columns:
        terms.update(column.name.lower().split("_"))
    return terms
