import uuid
from datetime import datetime, timezone
from typing import Any

data: list[dict[str, Any]] = [
    {
        "id": str(uuid.uuid4()),
        "feature_name": "work_packages",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "map",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "learnings",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "planning",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "forms_list",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "insights",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "admin",
        "created_at": datetime.now(timezone.utc),
        "configurations": {"tab": True},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "jsb",
        "created_at": datetime.now(timezone.utc),
        "configurations": {},
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "id": str(uuid.uuid4()),
        "feature_name": "ebo",
        "created_at": datetime.now(timezone.utc),
        "configurations": {},
        "updated_at": datetime.now(timezone.utc),
    },
]
