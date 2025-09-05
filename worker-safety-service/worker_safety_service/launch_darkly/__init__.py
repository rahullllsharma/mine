from worker_safety_service.config import settings

from .launch_darkly_client import LaunchDarklyClient


async def get_launch_darkly_client() -> LaunchDarklyClient:
    return LaunchDarklyClient(settings.LAUNCH_DARKLY_SDK_KEY)


__all__ = ["LaunchDarklyClient", "get_launch_darkly_client"]
