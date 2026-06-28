from collections.abc import Callable
from typing import Protocol

from app.core.config import Settings
from app.core.errors import ConfigurationError
from app.core.logging import get_logger
from app.services.llm.gemini_client import GeminiChatClient
from app.services.llm.groq_client import GroqChatClient

logger = get_logger(__name__)


class LLMClient(Protocol):
    async def ainvoke_text(self, prompt: str) -> str:
        ...

    @property
    def provider(self) -> str:
        ...

    @property
    def model(self) -> str:
        ...


class FallbackChatClient:
    def __init__(self, primary: LLMClient, fallback_factory: Callable[[], LLMClient]) -> None:
        self.primary = primary
        self.fallback_factory = fallback_factory
        self._fallback_client: LLMClient | None = None
        self._used_client = primary

    async def ainvoke_text(self, prompt: str) -> str:
        try:
            res = await self.primary.ainvoke_text(prompt)
            self._used_client = self.primary
            return res
        except Exception as exc:
            logger.warning("Primary LLM client failed: %s. Attempting fallback...", exc)
            try:
                if self._fallback_client is None:
                    self._fallback_client = self.fallback_factory()
                res = await self._fallback_client.ainvoke_text(prompt)
                self._used_client = self._fallback_client
                return res
            except Exception as fallback_exc:
                logger.error("Fallback LLM client also failed: %s", fallback_exc)
                raise fallback_exc

    @property
    def provider(self) -> str:
        return self._used_client.provider

    @property
    def model(self) -> str:
        return self._used_client.model


def _create_raw_client(provider: str, model: str, settings: Settings) -> LLMClient:
    if provider == "gemini":
        return GeminiChatClient(settings, model)
    elif provider == "groq":
        return GroqChatClient(settings, model)
    else:
        raise ConfigurationError(f"Unsupported provider: {provider}")


def get_llm_client(
    provider: str | None, model: str | None, settings: Settings
) -> LLMClient:
    primary_provider = provider or settings.default_provider
    primary_model = model or settings.default_model

    # Determine fallback provider and model
    if primary_provider == "gemini":
        fallback_provider = "groq"
        fallback_model = settings.default_model
    elif primary_provider == "groq":
        fallback_provider = "gemini"
        fallback_model = settings.fallback_model
    else:
        fallback_provider = "gemini"
        fallback_model = settings.default_model

    def fallback_factory() -> LLMClient:
        return _create_raw_client(fallback_provider, fallback_model, settings)

    try:
        primary_client = _create_raw_client(primary_provider, primary_model, settings)
        return FallbackChatClient(primary_client, fallback_factory)
    except ConfigurationError as exc:
        logger.warning(
            "Primary client configuration failed: %s. Falling back immediately.", exc
        )
        return fallback_factory()
