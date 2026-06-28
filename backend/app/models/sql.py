from pydantic import BaseModel, Field


class SQLColumn(BaseModel):
    name: str
    data_type: str


class SQLTableSchema(BaseModel):
    table_name: str
    columns: list[SQLColumn]


class GeneratedSQLQuery(BaseModel):
    sql: str
    parameters: list[str | int | float | bool | None] = Field(default_factory=list)
    table_name: str
    reasoning: str


class ValidatedSQLQuery(BaseModel):
    sql: str
    parameters: list[str | int | float | bool | None]
    table_name: str
