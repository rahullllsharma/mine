import uuid

from sqlmodel import Column, Field, Index, String, UniqueConstraint

from worker_safety_service.models.base import AbstractBaseModel


class JSBSupervisorLink(AbstractBaseModel, table=True):
    __tablename__ = "jsb_supervisor_link"
    __table_args__ = (
        Index("jsb_id_supervisor_id_index_unique", "manager_id", "jsb_id", unique=True),
        UniqueConstraint(
            "manager_id", "jsb_id", name="jsb_id_supervisor_id_contraint_unique"
        ),
    )

    jsb_id: uuid.UUID = Field(foreign_key="jsbs.id", nullable=False)
    manager_id: str = Field(nullable=False)
    manager_name: str = Field(sa_column=Column(String, nullable=True))
    manager_email: str = Field(sa_column=Column(String, nullable=True))
