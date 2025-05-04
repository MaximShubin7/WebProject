from pydantic import BaseModel, Field, validator
from uuid import UUID


class EstablishmentTypeValidator:
    @validator("establishment_type")
    def validate_establishment_type(cls, v):
        if v not in ["Кафе", "Столовая", "Ресторан", "Пекарня", "Пиццерия", "Кофейня", "Чайная", "Быстрое питание"]:
            raise ValueError("wrong type of establishment")
        return v


class EstablishmentTypeCreate(BaseModel, EstablishmentTypeValidator):
    establishment_type: str


class EstablishmentTypeUpdate(EstablishmentTypeCreate):
    establishment_type_id: UUID


class EstablishmentTypeResponse(EstablishmentTypeUpdate):
    pass
