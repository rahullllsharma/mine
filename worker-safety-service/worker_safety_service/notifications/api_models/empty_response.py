from pydantic import BaseModel


class EmptyResponse(BaseModel):
    ...

    class Config:
        extra = "forbid"
