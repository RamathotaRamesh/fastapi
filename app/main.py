from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users,login
from database import connect, disconnect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="FastAPI Backend",
    description="My FastAPI backend with MongoDB",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/v1", tags=["users"])
app.include_router(login.router, prefix="/v1", tags=["login"])


@app.on_event("startup")
async def startup_event():
    await connect()
    print("📱 FastAPI app started!")


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect()
    print("👋 FastAPI app stopped!")

@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Backend",
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}