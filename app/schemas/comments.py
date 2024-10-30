from typing import Optional

from pydantic import BaseModel, conint


class CommentSchemaAdd(BaseModel):
    owner_id: conint(ge=1) 

    class Config:
        from_attributes = True

class CommentSchemaUpdate(BaseModel):
    description: Optional[str] = None
   

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: conint(ge=1)
    owner_id: int

    class Config:
        from_attributes = True
