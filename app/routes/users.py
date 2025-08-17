from fastapi import APIRouter

router = APIRouter(
    prefix="/users",      
    tags=["Users"]
)

@router.get("/")
async def get_users():
    return {"message": "List of all users"}

# Example endpoint: get a single user by ID
@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"Details of user {user_id}"}

# Example endpoint: create a new user
@router.post("/")
async def create_user(name: str, email: str):
    return {"message": f"User {name} with email {email} created successfully"}

