# app/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import settings
from .models.session import get_user_session
from .routers import items

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)


@app.get("/")
async def root():
    return {"message": str(get_user_session("u1"))}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/images/{user_id}/{story_id}/{image_id}")
async def get_image(user_id: str, story_id: str, image_id: str):
    image_path = f"/etc/images/{user_id}/{story_id}/{image_id}.png"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}
