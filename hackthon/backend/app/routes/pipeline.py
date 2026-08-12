from pathlib import Path
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.pipeline_service import process_audio_to_slides


router = APIRouter(
    prefix="/api/pipeline",
    tags=["Pipeline"],
)


@router.post("/test")
async def test_pipeline(
    file: UploadFile = File(...),
):
    """
    Temporary endpoint for testing:

    Audio → Whisper → Transcript → Qwen → Slides → PPTX
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

        result = await process_audio_to_slides(file_path)

        return {
            "success": True,
            "filename": file.filename,
            **result,
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

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {exc}",
        )

    finally:
        if file_path.exists():
            file_path.unlink()


@router.get("/download/{filename}")
async def download_pptx(filename: str):
    """
    Download a generated PowerPoint presentation.
    """

    generated_dir = Path("generated").resolve()

    # Prevent paths such as ../../something.pptx
    safe_filename = Path(filename).name

    file_path = generated_dir / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PowerPoint file not found.",
        )

    if file_path.suffix.lower() != ".pptx":
        raise HTTPException(
            status_code=400,
            detail="Only PPTX files can be downloaded.",
        )

    return FileResponse(
        path=file_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
        filename=safe_filename,
    )