# app/main.py
import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

from .config import settings
from .models.db import Base, engine
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
def on_startup():
    Base.metadata.create_all(bind=engine)


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
