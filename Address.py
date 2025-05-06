from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class AddressCreate(BaseModel):
    address: str
    latitude: float
    longitude: float


class AddressUpdate(BaseModel):
    address_id: UUID
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class AddressResponse(AddressCreate):
    address_id: UUID
