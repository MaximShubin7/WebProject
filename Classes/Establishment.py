from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from Classes.Address import AddressResponse, AddressCreate, AddressUpdate


class EstablishmentCreate(BaseModel):
    address: AddressCreate
    name: str
    rating: Optional[float] = Field(None, ge=1, le=5)
    count_comment: int = Field(0, ge=0)
    contacts: Optional[str] = None
    official_website: Optional[str] = None
    social_links: Optional[str] = None
    working_hours: Optional[str] = None


class EstablishmentUpdate(EstablishmentCreate):
    establishment_id: UUID
    address: Optional[AddressUpdate] = None
    name: Optional[str]


class EstablishmentAddressResponse(BaseModel):
    establishment_id: UUID
    name: str
    address: AddressResponse


class EstablishmentResponse(EstablishmentCreate):
    establishment_id: UUID
    address: AddressResponse
