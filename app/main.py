# app/main.py
import logging
import os

from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("/etc/logs", exist_ok=True)

# Configure logging with both file and console handlers
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

# File handler (your existing setup)
try:
    file_handler = RotatingFileHandler(
        filename="/etc/logs/app.log",
        mode="a",
        maxBytes=1024 * 1000,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    print("File logging configured: /etc/logs/app.log")
except Exception as e:
    print(f"File logging failed: {e}")

# Console handler (NEW - this will show logs in your terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)  # You can change to DEBUG for more verbose
logger.addHandler(console_handler)
print("SUCCESS - Console logging configured")


from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

from .config import settings
from .models.db import init_models, load_achievements_from_json, load_settings_from_json
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


@app.on_event("startup")
async def on_startup():
    await init_models()
    await load_settings_from_json()
    await load_achievements_from_json()


@app.get("/")
async def root():
    return {"message": "connected to the server..."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/images/{user_id}/{story_id}/{image_id}")
async def get_image(user_id: str, story_id: str, image_id: str):
    image_path = f"/etc/images/{user_id}/{story_id}/{image_id}.png"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}


@app.get("/audio/{user_id}/{story_id}/{audio_id}")
async def get_audio(user_id: str, story_id: str, audio_id: str):
    audio_path = f"/etc/audio/{user_id}/{story_id}/{audio_id}.wav"
    if os.path.exists(audio_path):
        return FileResponse(audio_path)
    return {"error": "Audio not found"}


@app.get("/assets/logos/{image_id}")
async def get_image(image_id: str):
    image_path = f"/app/app/assets/logos/{image_id}.png"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation Error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )
