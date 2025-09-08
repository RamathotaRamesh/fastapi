# schemas/auth_schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional

class GetOTPRequest(BaseModel):
    email: EmailStr

class SubmitOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPResponse(BaseModel):
    message: str
    status: str
    expires_at: Optional[str] = None

class LoginResponse(BaseModel):
    message: str
    status: str
    user_data: Optional[dict] = None
    access_token: Optional[str] = None