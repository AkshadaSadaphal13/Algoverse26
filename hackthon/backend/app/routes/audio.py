import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.job import Job
from app.schemas.job import JobCreateResponse
from app.services.audio_service import get_audio_duration_seconds
from app.services.pricing_service import calculate_usage_and_price
from app.utils.file_utils import is_allowed_file, save_upload, secure_filename

router = APIRouter(prefix="/api/jobs")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=JobCreateResponse)
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not is_allowed_file(file.filename, file.content_type):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid audio file type.")

    stored_name = secure_filename(file.filename)
    upload_path = Path(settings.uploads_dir) / stored_name

    try:
        saved_path, size = save_upload(file, upload_path)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc))

    job_id = str(uuid.uuid4())
    duration_seconds = get_audio_duration_seconds(Path(saved_path))
    pricing = calculate_usage_and_price(duration_seconds)

    job = Job(
        job_id=job_id,
        original_filename=file.filename,
        stored_filename=stored_name,
        mime_type=file.content_type,
        file_size=size,
        audio_duration_seconds=duration_seconds,
        usage_minutes=pricing['usage_minutes'],
        price_usdc=pricing['price_usdc'],
        payment_status="pending",
        processing_status="uploaded",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobCreateResponse.from_orm(job)
