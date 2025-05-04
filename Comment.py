from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class CommentCreate(BaseModel):
    user_id: UUID
    establishment_id: UUID
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = Field(None, min_length=10, max_length=500)


class CommentUpdate(BaseModel):
    comment_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: Optional[str] = Field(None, min_length=10, max_length=500)


class CommentResponse(CommentCreate):
    comment_id: UUID
    created_at: datetime
