from pydantic import BaseModel, Field, validator
from typing import Dict
from uuid import UUID


class MenuValidator:
    @validator("menu")
    def validate_key_length(cls, v: Dict[str, float]) -> Dict[str, float]:
        if not all(len(key) < 50 for key in v.keys()):
            raise ValueError("The name of the menu item should not be longer than 50 characters")
        return {key: round(val, 2) for key, val in v.items()}


class MenuCreate(BaseModel, MenuValidator):
    menu: Dict[str, float]


class MenuUpdate(MenuCreate):
    menu_id: UUID


class MenuResponse(MenuUpdate):
    pass
