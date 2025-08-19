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
    user_id = 1 if not users_db else users_db[-1]["id"] + 1
    new_user = {"id": user_id, **user.model_dump()}
    users_db.append(new_user)
    return JSONResponse(
        status_code=201,
       content={"message": f"User {user_id} created successfully","data":new_user}
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate):
    for index, existing_user in enumerate(users_db):
        if existing_user["id"] == user_id:
            updated_user = {"id": user_id, **user.model_dump()}
            users_db[index] = updated_user
            return JSONResponse(
                status_code=200,
                content={"message": f"User {user_id} updated successfully", "data": updated_user}
            )


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    global users_db
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            del users_db[index]
            return JSONResponse(
                status_code=200,
                content={"message": f"User {user_id} deleted successfully"}
            )