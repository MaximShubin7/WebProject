from datetime import datetime

from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID


class CommentValidator:
    @validator("created_time")
    def validate_created_time(cls, v):
        return v.strftime("%Y-%m-%d %H:%M")


class CommentCreate(BaseModel):
    user_id: UUID
    establishment_id: UUID
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None


class CommentUpdate(BaseModel):
    comment_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: Optional[str] = None


class CommentResponse(CommentCreate, CommentValidator):
    comment_id: UUID
    created_time: datetime
