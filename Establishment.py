from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional
from datetime import time
from uuid import UUID


class EstablishmentValidator:
    @validator("working_hours")
    def validate_working_hours(cls, v):
        if v is None:
            return None

        if len(v) != 7:
            raise ValueError("There should be 7 elements (days of the week)")

        for day in v:
            try:
                open_time, close_time = day.split('-')
                time.fromisoformat(open_time.strip())
                time.fromisoformat(close_time.strip())
            except ValueError:
                raise ValueError('The time format should be "HH:MM-HH:MM"')
        return v


class EstablishmentCreate(BaseModel, EstablishmentValidator):
    establishment_type_id: UUID
    address_id: UUID
    menu_id: Optional[UUID] = None
    rating: Optional[float] = Field(None, ge=1, le=5, pattern=r'^\d\.\d$')
    count_comment: int = Field(0, ge=0)
    official_website: Optional[HttpUrl] = None
    working_hours: List[str]
    average_check: Optional[float] = Field(None, ge=100)


class EstablishmentUpdate(EstablishmentCreate):
    establishment_id: UUID
    establishment_type_id: Optional[UUID] = None
    address_id: Optional[UUID] = None
    count_comment: Optional[int] = Field(None, ge=0)
    working_hours: Optional[List[str]] = None


class EstablishmentResponse(EstablishmentCreate):
    establishment_id: UUID
