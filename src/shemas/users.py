from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from src.core.constants import UserType, UserRole


class UserCreate(BaseModel):
    name: str = Field(..., max_length=255)
    password: str = Field(..., min_length=5)
    type: UserType
    role: UserRole = UserRole.employee
    shortname: Optional[str] = None
    tin: Optional[str] = None
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    brand: Optional[str] = None
    manager_name: Optional[str] = None
    manager_position: Optional[str] = None

class UserPatch(BaseModel):
    shortname: Optional[str] = None
    role: Optional[UserRole] = None
    tin: Optional[str] = None
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    brand: Optional[str] = None
    manager_name: Optional[str] = None
    manager_position: Optional[str] = None

class UserRead(BaseModel):
    id: UUID
    name: str
    type: UserType
    role: UserRole
    class Config:
        from_attributes = True
