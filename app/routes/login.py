# routes/auth_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database import get_database
from datetime import datetime, timedelta
import base64
import json
import logging
import hmac
import hashlib

from app.schemas.login import (
    GetOTPRequest, 
    SubmitOTPRequest, 
    OTPResponse, 
    LoginResponse
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/login", tags=["Authentication"])

# Constants
OTP_EXPIRY_MINUTES = 1
MAX_OTP_ATTEMPTS = 3

def generate_otp_from_phone(phone_number):
    phone_str = str(phone_number)
    if len(phone_str) >= 6:
        return phone_str[-6:]
    else:
        return phone_str.zfill(6)

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def base64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

def generate_access_token(user_data):
    
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    payload = {
        "userId": user_data.get("userId"),
        "email": user_data.get("email"),
        "iat": int(datetime.now().timestamp()),
        "exp": int((datetime.now() + timedelta(hours=24)).timestamp())
    }
    
    header_encoded = base64url_encode(json.dumps(header).encode())
    payload_encoded = base64url_encode(json.dumps(payload).encode())
    
    secret_key = "MyOtpApp2024SecretKey!@#Secure"
    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_encoded = base64url_encode(signature)
    jwt_token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
    return jwt_token

@router.post("/get_otp", response_model=OTPResponse)
async def get_otp(request: GetOTPRequest):
    try:
        database = get_database()
        email = request.email
        
        user = await database.users.find_one({"email": email})
        if not user:
            return JSONResponse(
                status_code=404,
                content={"message": "User not found, Please register first."}
            )
        
        phone_number = user.get("phoneNumber")
        if not phone_number:
            return JSONResponse(
                status_code=404,
                content={"message": "Phone number not found for this user."}
            )
        
        otp = generate_otp_from_phone(phone_number)
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        otp_doc = {
            "email": email,
            "otp": otp,
            "attempts": 0,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_used": False
        }
        
        await database.otps.delete_many({"email": email})
        
        await database.otps.insert_one(otp_doc)
        
        return OTPResponse(
            message=f"Your OTP is: {otp} (last 6 digits of your phone number)",
            status="success",
            expires_at=expires_at.strftime("%d-%m-%Y %H:%M:%S")
        )
    except Exception as e:
        logger.error(f"Error in get_otp: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Failed to generate OTP",
                "status": "error",
                "detail": str(e)
            }
        )

@router.post("/submit_otp", response_model=LoginResponse)
async def submit_otp(request: SubmitOTPRequest):
    try:
        database = get_database()
        email = request.email
        provided_otp = request.otp
        
        otp_record = await database.otps.find_one({
            "email": email,
            "expires_at": {"$gt": datetime.now()},
            "is_used": False
        })
        
        if not otp_record:
            return JSONResponse(
                status_code=404,
                content={"message": "OTP not found or expired"}
            )
        
        if provided_otp != otp_record["otp"]:
            await database.otps.update_one(
                {"_id": otp_record["_id"]},
                {"$inc": {"attempts": 1}}
            )
            
            remaining_attempts = MAX_OTP_ATTEMPTS - (otp_record["attempts"] + 1)
            if remaining_attempts > 0:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": f"Invalid OTP. You have {remaining_attempts} attempts left."
                    }
                )
            else:
                await database.otps.delete_one({"_id": otp_record["_id"]})
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "Maximum OTP attempts exceeded. Please request a new OTP."
                    }
                )
        
        user = await database.users.find_one({"email": email})
        
        await database.otps.update_one(
            {"_id": otp_record["_id"]},
            {"$set": {"is_used": True, "used_at": datetime.now()}}
        )
        
        user_data = {
            "userId": user.get("userId"),
            "fullName":user.get("fullName"),
            "email": user.get("email"),
            "phoneNumber": user.get("phoneNumber"),
            "age": user.get("age")
        }
        
        access_token = generate_access_token(user_data)
        
        await database.users.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.now()}}
        )
        
        return LoginResponse(
            message="Login successful",
            status="success",
            user_data=user_data,
            access_token=access_token
        )
        
    except Exception as e:
        logger.error(f"Error in submit_otp: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Failed to submit OTP",
                "status": "error",
                "detail": str(e)
            }
        )