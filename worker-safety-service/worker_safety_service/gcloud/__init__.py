from typing import Generator

from worker_safety_service.gcloud.storage import FileStorage, file_storage


def get_file_storage() -> Generator:
    yield file_storage


__all__ = [
    "get_file_storage",
    "file_storage",
    "FileStorage",
]
