"""
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes
"""

from typing import Any

from fastapi import APIRouter

from worker_safety_service.config import settings

router = APIRouter()


@router.get(
    "/readyz",
    openapi_extra={"security": []},
)
async def readyz() -> dict[str, Any]:
    """Readyness probe

    Indicates whether the service is able to handle requests.
    """
    return {"message": "OK", "version": settings.APP_VERSION}


@router.get(
    "/livez",
    openapi_extra={"security": []},
)
async def livez() -> dict[str, Any]:
    """Liveness && Startup Probe

    Indicates whether the service is running.
    """
    return {"message": "OK", "version": settings.APP_VERSION}
