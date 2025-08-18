from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

class UserCreate(UserBase):
    name: str
    email: EmailStr
    age: Optional[int] = None

class UserResponse(UserBase):
    id: int
