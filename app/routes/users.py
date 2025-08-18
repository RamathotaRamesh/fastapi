from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
from app.schemas.users import UserCreate, UserResponse 

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

users_db = []

@router.get("/", response_model=List[UserResponse])
async def get_users():
    return JSONResponse(
        status_code=200,
        content={"data":users_db,"message":"Users Data Fetch Successfully"}
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return JSONResponse(
                status_code=200,
                content={"data":user,"message":f"{user_id} details fetched successfully"}
            )
    return JSONResponse(
        status_code=404,
       content={"message": f"User {user_id} not found"}
    )

@router.post("/add", response_model=UserResponse)
async def create_user(user: UserCreate):
    user_id = len(users_db) + 1
    new_user = {"id": user_id, **user.model_dump()}
    users_db.append(new_user)
    return JSONResponse(
        status_code=201,
       content={"message": f"User {user_id} created successfully","data":new_user}
    )


