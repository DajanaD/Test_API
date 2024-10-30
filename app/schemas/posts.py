from operator import ge
from pydantic import BaseModel, conint
from enum import Enum


class PostSchemaAdd(BaseModel):
    owner_id: conint(ge=1)

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: conint(ge=1)
    comment_id: int

    class Config:
        from_attributes = True


class PostLiteResponse(BaseModel):
    id: conint(ge=1)
    comment_id: int

    class Config:
        from_attributes = True


class PostPeriod(Enum):
    WEEK = "тиждень"
    MONTH = "місяць"
    YEAR = "рік"
    ALL = "вся історія пocтів"
