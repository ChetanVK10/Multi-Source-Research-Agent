from pydantic import BaseModel

from app.models.citations import Citation


class SynthesisResult(BaseModel):
    answer: str
    citations: list[Citation]
