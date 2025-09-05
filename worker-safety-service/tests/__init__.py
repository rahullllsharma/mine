from worker_safety_service.config import settings

if not settings.POSTGRES_APPLICATION_NAME:
    settings.POSTGRES_APPLICATION_NAME = "tests"
