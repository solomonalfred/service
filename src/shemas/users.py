from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, SecretStr
from src.core.constants import UserType, UserRole


class UserBase(BaseModel):
    type: UserType = Field(..., description="LE / NP / IE / SE")
    role: UserRole = UserRole.employee
    name: str
    shortname: Optional[str] = None
    tin: Optional[str] = None
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    brand: Optional[str] = None
    manager_name: Optional[str] = None
    manager_position: Optional[str] = None

class UserInfo(UserBase):
    password_hash: SecretStr

class UserPatch(BaseModel):
    role: Optional[UserRole] = None
    shortname: Optional[str] = None
    tin: Optional[str]= None
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    brand: Optional[str] = None
    manager_name: Optional[str] = None
    manager_position:Optional[str] = None
    password: Optional[SecretStr] = None

class UserRead(UserBase):
    id: UUID
    class Config:
        from_attributes = True
