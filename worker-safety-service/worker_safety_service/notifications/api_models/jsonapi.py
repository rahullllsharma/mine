import uuid
from typing import Any, Optional, Sequence

from pydantic import BaseModel, Field


class Links(BaseModel):
    # Pagination
    next: Optional[str] = None
    self_link: Optional[str] = Field(default=None, alias="self")
    related: Optional[str] = None

    def dict(self, **kwargs: Any) -> Any:
        """Remove unset attributes so that we do not send empty data in a response"""
        if not kwargs:
            kwargs = {}
        kwargs["exclude_unset"] = True
        return super(Links, self).dict(**kwargs)


class Meta(BaseModel):
    limit: Optional[int] = None

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        """Remove unset attributes so that we do not send empty data in a response"""
        if not kwargs:
            kwargs = {}
        kwargs["exclude_unset"] = True
        return super(Meta, self).dict(**kwargs)


class ModelRequest(BaseModel):
    type: str
    attributes: BaseModel


class ModelResponse(ModelRequest):
    id: uuid.UUID


class Response(BaseModel):
    links: Links = Field(default_factory=Links)
    data: ModelResponse


class BulkResponse(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    links: Links = Field(default_factory=Links)
    data: Sequence[ModelResponse]


class RelationshipData(BaseModel):
    type: str
    id: uuid.UUID


class ManyToOneRelation(BaseModel):
    links: Links


class OneToOneRelation(BaseModel):
    data: RelationshipData
    links: Optional[Links] = None
