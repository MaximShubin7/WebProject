from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from uuid import UUID
import bcrypt


class UserValidator:
    @validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return bcrypt.hashpw(v.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @validator("phone_number")
    def validate_phone_number(cls, v: str) -> str:
        return v if v[0] == '+' else '+7' + v[1:]


class UserCreate(BaseModel, UserValidator):
    name: Optional[str] = None
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(None, pattern=r'^(\+7|7|8)\d{10}$')


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(UserCreate):
    user_id: UUID
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    user_id: UUID
    name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    bonus: float
