from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError


class GroqChatClient:
    def __init__(self, settings: Settings, model: str | None = None) -> None:
        if settings.groq_api_key is None or len(settings.groq_api_key.get_secret_value().strip()) == 0:
            raise ConfigurationError("GROQ_API_KEY is required for answer synthesis.")

        from langchain_groq import ChatGroq

        self._model = model or "llama-3.3-70b-versatile"
        self._client = ChatGroq(
            model=self._model,
            groq_api_key=settings.groq_api_key.get_secret_value(),
            temperature=0.1,
        )

    @property
    def provider(self) -> str:
        return "groq"

    @property
    def model(self) -> str:
        return self._model

    async def ainvoke_text(self, prompt: str) -> str:
        try:
            response = await self._client.ainvoke(prompt)
        except Exception as exc:
            raise ExternalToolError(f"Groq synthesis failed: {exc}") from exc

        content = getattr(response, "content", "")
        if isinstance(content, str):
            return content.strip()
        return str(content).strip()
