from enum import Enum


class ObjectType(Enum):
    JobSafetyBriefing = "jsb"
    EnergyBasedObservation = "ebo"
    DailyReport = "dir"


class EventType(Enum):
    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    COMPLETE = "complete"
    REOPEN = "reopen"
