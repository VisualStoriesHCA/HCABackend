# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models.session import create_user_session, get_user_session
from .routers import items

create_user_session("u1", "Rifat")

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
