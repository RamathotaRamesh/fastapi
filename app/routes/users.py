
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any
from app.schemas.users import UserCreate 
from database import get_database
from app.utils.FormatDate import format_date

router = APIRouter(prefix="/users", tags=["users"])

_db_cache = None

def get_db():
    global _db_cache
    if _db_cache is None:
        _db_cache = get_database()
    return _db_cache

def format_user(user: Dict[str, Any]) -> Dict[str, Any]:
    if user:
        user["_id"] = str(user["_id"])
        user["createdDate"] = format_date(user.get("createdDate"))
        user["lastModifiedDate"] = format_date(user.get("lastModifiedDate"))
    return user

_last_user_id_cache = None
_cache_time = None

async def get_next_user_id(db):
    
    global _last_user_id_cache, _cache_time
    
    if _last_user_id_cache and _cache_time and (datetime.now() - _cache_time).seconds < 5:
        numeric_part = int(_last_user_id_cache.replace("USER", ""))
        next_id = f"USER{numeric_part + 1:03d}"
        _last_user_id_cache = next_id
        return next_id
    
    last_user = await db.users.find_one(
        sort=[("userId", -1)],
        projection={"userId": 1} 
    )
    
    if last_user and "userId" in last_user:
        last_id = last_user["userId"]
        numeric_part = int(last_id[4:])
        next_id = f"USER{numeric_part + 1:03d}"
    else:
        next_id = "USER001"
    
    _last_user_id_cache = next_id
    _cache_time = datetime.now()
    return next_id

@router.get("/")
async def get_users():
    try:
        db = get_db()
        
        users = await db.users.find({}).to_list(length=1000)
        formatted_users = [format_user(user) for user in users]
        return JSONResponse(
            status_code=200,
            content={
                "data": formatted_users,
                "message": "Users fetched successfully",
                "totalCount": len(formatted_users),
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to fetch users: {str(e)}",
                "status": "error"
            }
        )

@router.get("/{userId}")
async def get_user(userId: str):
    try:
        db = get_db()
        user = await db.users.find_one({"userId": userId})
        
        if not user:
            return JSONResponse(
                status_code=404,
                content={"message": f"User with ID {userId} not found"}
            )
        
        formatted_user = format_user(user)
        
        return JSONResponse(
            status_code=200,
            content={
                "data": formatted_user,
                "message": f"{userId} fetched successfully"
            }
        )
        
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "message": f"Failed to fetch user: {str(error)}"
            }
        )

@router.post("/add", response_model=dict)
async def create_user(user: UserCreate):
    """Create user - optimized with single duplicate check"""
    try:
        db = get_db()
        
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user.email},
                {"phoneNumber": user.phoneNumber}
            ]
        }, projection={"email": 1, "phoneNumber": 1})
        
        if existing_user:
            duplicate_field = "Email" if existing_user.get("email") == user.email else "Phone Number"
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"{duplicate_field} already exists",
                    "status": "failed"
                }
            )
        
        userId = await get_next_user_id(db)
        current_time = datetime.now()
        
        user_doc = user.model_dump()
        user_doc.update({
            "userId": userId,
            "createdDate": current_time,
            "lastModifiedDate": current_time
        })
        
        result = await db.users.insert_one(user_doc)
        
        user_doc["_id"] = str(result.inserted_id)
        formatted_user = format_user(user_doc)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "User created successfully",
                "id": userId,
                "data": formatted_user
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to create user: {str(e)}",
                "status": "failed"
            }
        )

@router.put("/{userId}")
async def update_user(userId: str, user: UserCreate):
    try:
        db = get_db()
        
        update_data = user.model_dump(exclude_unset=True, exclude_none=True)
        update_data["lastModifiedDate"] = datetime.now()
        
        updated_user = await db.users.find_one_and_update(
            {"userId": userId},
            {"$set": update_data},
            return_document=True
        )
        
        if not updated_user:
            return JSONResponse(
                status_code=404,
                content={"message": f"User with ID {userId} not found"}
            )
        
        formatted_user = format_user(updated_user)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "User updated successfully",
                "data": formatted_user,
                "status": "success"
            }
        )
        
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to update user: {str(error)}",
                "status": "failed"
            }
        )

@router.delete("/{userId}")
async def delete_user(userId: str):
    try:
        db = get_db()
        
        result = await db.users.find_one_and_delete({"userId": userId})
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={"message": f"User with ID {userId} not found"}
            )
        
        return JSONResponse(
            status_code=200,
            content={"message": f"{userId} deleted successfully"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to delete user: {str(e)}",
                "status": "failed"
            }
        )