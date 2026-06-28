from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.models.responses import ProviderConfigResponse
from app.services.llm.registry import get_available_models

router = APIRouter()


@router.get(
    "",
    response_model=list[ProviderConfigResponse],
    summary="Get list of supported LLM models and providers",
)
async def list_models(settings: SettingsDep) -> list[ProviderConfigResponse]:
    return get_available_models(settings)
