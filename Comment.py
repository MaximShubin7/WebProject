from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class CommentCreate(BaseModel):
    user_id: UUID
    establishment_id: UUID
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None


class CommentUpdate(BaseModel):
    comment_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: Optional[str] = None


class CommentResponse(CommentCreate):
    comment_id: UUID
    created_time: str
