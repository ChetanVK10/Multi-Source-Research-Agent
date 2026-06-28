from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.models.responses import HealthResponse
from app.services.health import check_dependencies

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check application and dependency health",
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    services = await check_dependencies(settings)

    overall_status = "ok"

    for service in services.values():
        # Ignore optional services that are simply not configured.
        if service.status == "unconfigured":
            continue

        # Any actual degraded dependency makes the app degraded.
        if service.status == "degraded":
            overall_status = "degraded"
            break

    return HealthResponse(
        status=overall_status,
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.app_env,
        services=services,
    )