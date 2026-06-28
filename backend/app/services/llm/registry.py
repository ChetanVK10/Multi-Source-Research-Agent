import logging

from pydantic import BaseModel

from app.core.config import Settings

logger = logging.getLogger(__name__)

class ModelConfig(BaseModel):
    id: str
    name: str

class ProviderConfig(BaseModel):
    id: str
    name: str
    models: list[ModelConfig]
    is_available: bool

SUPPORTED_PROVIDERS = [
    {
        "id": "gemini",
        "name": "Gemini",
        "models": [
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
        ],
    },
    {
        "id": "groq",
        "name": "Groq",
        "models": [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
            {"id": "deepseek-r1-distill-llama-70b", "name": "DeepSeek R1 Distill Llama 70B"},
            {"id": "qwen-qwq-32b", "name": "Qwen QWQ 32B"},
        ],
    },
]

def get_available_models(settings: Settings) -> list[ProviderConfig]:
    """Return list of providers with availability based on Settings.

    Checks that the required API keys are present and non‑empty.
    """
    logger.debug("Fetching available models with settings: %s", settings)
    results: list[ProviderConfig] = []
    for prov in SUPPORTED_PROVIDERS:
        is_avail = False
        if prov["id"] == "gemini":
            api_key = settings.gemini_api_key
            is_avail = api_key is not None and len(api_key.get_secret_value().strip()) > 0
        elif prov["id"] == "groq":
            api_key = settings.groq_api_key
            is_avail = api_key is not None and len(api_key.get_secret_value().strip()) > 0
            logger.debug("Groq api_key present: %s, is_available: %s", bool(api_key), is_avail)
        models = [ModelConfig(**m) for m in prov["models"]]
        results.append(
            ProviderConfig(
                id=prov["id"],
                name=prov["name"],
                models=models,
                is_available=is_avail,
            )
        )
    return results
