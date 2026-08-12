from pydantic import BaseModel, ConfigDict


class JobCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    original_filename: str
    mime_type: str
    file_size: int
    audio_duration_seconds: float | None = None
    usage_minutes: float | None = None
    price_usdc: float | None = None
    payment_status: str
    processing_status: str


class JobResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    original_filename: str
    price_usdc: float | None = None
    payment_status: str
    processing_status: str
    result_summary: str | None = None
