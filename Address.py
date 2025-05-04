from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class AddressCreate(BaseModel):
    country: str = Field(..., max_length=30)
    region: str = Field(..., max_length=30)
    city: str = Field(..., max_length=30)
    street: str = Field(..., max_length=30)
    house_number: str = Field(..., max_length=30)
    building: str = Field(None, max_length=5)
    floor: Optional[int] = None
    postal_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    latitude: float = Field(..., pattern=r'^-?(90|\d{1,2})(\.\d{1,6})?$')
    longitude: float = Field(..., pattern=r'^-?(180|\d{1,3})(\.\d{1,6})?$')


class AddressUpdate(AddressCreate):
    address_id: UUID
    country: Optional[str] = Field(None, max_length=30)
    region: Optional[str] = Field(None, max_length=30)
    city: Optional[str] = Field(None, max_length=30)
    street: Optional[str] = Field(None, max_length=30)
    house_number: Optional[str] = Field(None, max_length=30)
    postal_code: Optional[str] = Field(None, min_length=6, max_length=6, pattern=r'^\d{6}$')
    latitude: Optional[float] = Field(None, pattern=r'^-?(90|\d{1,2})(\.\d{1,6})?$')
    longitude: Optional[float] = Field(None, pattern=r'^-?(180|\d{1,3})(\.\d{1,6})?$')


class AddressResponse(AddressCreate):
    address_id: UUID
