from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    fullName: str
    email: EmailStr
    phoneNumber: int
    age: Optional[int] = None

class UserCreate(UserBase):
    fullName: str
    email: EmailStr
    phoneNumber: int
    age: Optional[int] = None


class UserResponse(BaseModel):
    userId: str
    fullName: str
    email: EmailStr
    phoneNumber: int
    age: Optional[int] = None
    created_time: str
    
    class Config:
        from_attributes = True  