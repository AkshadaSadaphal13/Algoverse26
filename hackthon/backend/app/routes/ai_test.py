from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import generate_insights


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class TranscriptRequest(BaseModel):
    transcript: str


@router.post("/test")
async def test_ai(request: TranscriptRequest):
    try:
        result = await generate_insights(request.transcript)

        return {
            "success": True,
            "model": "qwen2.5-7b-instruct",
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )