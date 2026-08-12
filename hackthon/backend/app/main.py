from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.audio import router as audio_router
from app.routes.health import router as health_router
from app.routes.payment import router as payment_router
from app.routes.ai_test import router as ai_test_router
from app.routes.transcription import router as transcription_router
from app.routes.pipeline import router as pipeline_router


app = FastAPI(
    title="CodeVerse Voice-to-Slide-Deck",
    version="0.1.0",
    description="Backend API for CodeVerse pay-per-use voice to slide deck generator.",
)


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes
app.include_router(health_router)
app.include_router(audio_router)
app.include_router(payment_router)
app.include_router(ai_test_router)
app.include_router(transcription_router)
app.include_router(pipeline_router)


# Create database tables
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)