from pathlib import Path
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.audio_service import transcribe_audio


router = APIRouter(
    prefix="/api/transcription",
    tags=["Transcription"],
)


@router.post("/test")
async def test_transcription(file: UploadFile = File(...)):
    """
    Temporary endpoint for testing speech-to-text.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio filename is required.",
        )

    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)

    safe_name = f"{uuid.uuid4()}_{Path(file.filename).name}"
    file_path = temp_dir / safe_name

    try:
        contents = await file.read()
        file_path.write_bytes(contents)

        transcript = transcribe_audio(file_path)

        return {
            "success": True,
            "filename": file.filename,
            "transcript": transcript,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {exc}",
        )

    finally:
        if file_path.exists():
            file_path.unlink()