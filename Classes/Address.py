from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class AddressCreate(BaseModel):
    address: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AddressUpdate(BaseModel):
    address_id: UUID
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class AddressResponse(AddressCreate):
    address_id: UUID
