from pydantic import BaseModel, Field
from typing import Optional

class FilterEstablishments(BaseModel):
    name: Optional[str] = None
    rating: Optional[float] = Field(None, ge=1, le=5)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)