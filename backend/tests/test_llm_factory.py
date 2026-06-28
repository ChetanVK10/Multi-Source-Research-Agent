import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import SecretStr

from app.core.config import Settings
from app.core.errors import ConfigurationError, ExternalToolError
from app.services.llm.registry import get_available_models
from app.services.llm.factory import get_llm_client, FallbackChatClient


def test_registry_availability():
    settings = Settings(
        gemini_api_key=SecretStr("mock-key"),
        groq_api_key=None,
    )
    models = get_available_models(settings)

    gemini_prov = next(p for p in models if p.id == "gemini")
    groq_prov = next(p for p in models if p.id == "groq")

    assert gemini_prov.is_available is True
    assert groq_prov.is_available is False


@patch("app.services.llm.factory.GeminiChatClient")
@patch("app.services.llm.factory.GroqChatClient")
def test_factory_initialization_routing(mock_groq, mock_gemini):
    settings = Settings(
        gemini_api_key=SecretStr("gemini-key"),
        groq_api_key=SecretStr("groq-key"),
    )

    client = get_llm_client(provider="gemini", model="gemini-2.5-flash", settings=settings)
    assert isinstance(client, FallbackChatClient)
    assert client.primary == mock_gemini.return_value

    mock_gemini.assert_called_once_with(settings, "gemini-2.5-flash")


@patch("app.services.llm.factory.GeminiChatClient")
@patch("app.services.llm.factory.GroqChatClient")
def test_factory_immediate_fallback_on_init_error(mock_groq, mock_gemini):
    # Simulate Groq key validation error raising ConfigurationError on creation
    mock_groq.side_effect = ConfigurationError("missing key")

    settings = Settings(
        gemini_api_key=SecretStr("gemini-key"),
        groq_api_key=None,
    )

    client = get_llm_client(provider="groq", model="llama-3.3-70b-versatile", settings=settings)

    # It should immediately route to gemini without raising error
    assert client == mock_gemini.return_value
    mock_gemini.assert_called_once_with(settings, "gemini-2.5-flash")


@pytest.mark.asyncio
async def test_fallback_client_runtime_failure():
    primary_client = MagicMock()
    primary_client.ainvoke_text = AsyncMock(side_effect=ExternalToolError("Rate limited"))
    primary_client.provider = "groq"
    primary_client.model = "llama-3.3-70b-versatile"

    fallback_client = MagicMock()
    fallback_client.ainvoke_text = AsyncMock(return_value="succeeded answer")
    fallback_client.provider = "gemini"
    fallback_client.model = "gemini-2.5-flash"

    fallback_factory = MagicMock(return_value=fallback_client)

    wrapper = FallbackChatClient(primary_client, fallback_factory)

    assert wrapper.provider == "groq"
    assert wrapper.model == "llama-3.3-70b-versatile"

    result = await wrapper.ainvoke_text("test prompt")

    assert result == "succeeded answer"
    primary_client.ainvoke_text.assert_called_once_with("test prompt")
    fallback_factory.assert_called_once()
    fallback_client.ainvoke_text.assert_called_once_with("test prompt")

    assert wrapper.provider == "gemini"
    assert wrapper.model == "gemini-2.5-flash"
