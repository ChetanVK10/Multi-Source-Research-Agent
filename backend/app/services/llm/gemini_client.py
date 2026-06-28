from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError


class GeminiChatClient:
    def __init__(self, settings: Settings, model: str | None = None) -> None:
        if settings.gemini_api_key is None or len(settings.gemini_api_key.get_secret_value().strip()) == 0:
            raise ConfigurationError("GEMINI_API_KEY is required for answer synthesis.")

        from langchain_google_genai import ChatGoogleGenerativeAI

        self._model = model or settings.gemini_model
        self._client = ChatGoogleGenerativeAI(
            model=self._model,
            google_api_key=settings.gemini_api_key.get_secret_value(),
            temperature=settings.gemini_temperature,
        )

    @property
    def provider(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    async def ainvoke_text(self, prompt: str) -> str:
        try:
            response = await self._client.ainvoke(prompt)
        except Exception as exc:
            raise ExternalToolError(f"Gemini synthesis failed: {exc}") from exc

        content = getattr(response, "content", "")
        if isinstance(content, str):
            return content.strip()
        return str(content).strip()
