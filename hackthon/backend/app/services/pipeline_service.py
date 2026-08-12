from pathlib import Path
from typing import Any
import uuid

from app.config import settings
from app.services.audio_service import transcribe_audio
from app.services.llm_service import generate_insights
from app.services.pptx_service import generate_pptx


async def process_audio_to_slides(
    file_path: Path,
) -> dict[str, Any]:

    print("\n==============================")
    print("CODEVERSE PIPELINE STARTED")
    print("==============================")

    # 1. Whisper
    print("[1/3] Starting audio transcription...")

    transcript = transcribe_audio(file_path)

    print("[1/3] Transcription completed.")
    print("Transcript:", transcript)

    # 2. Qwen
    print("[2/3] Sending transcript to Qwen...")

    ai_result = await generate_insights(transcript)

    print("[2/3] Qwen completed.")

    # 3. PowerPoint
    print("[3/3] Generating PowerPoint...")

    # Create unique PowerPoint filename
    original_name = Path(file_path).stem
    pptx_filename = (
        f"CodeVerse_{uuid.uuid4()}_{original_name}.pptx"
    )

    output_path = Path(settings.generated_dir) / pptx_filename

    generate_pptx(
        ai_result=ai_result,
        output_path=output_path,
    )

    print("[3/3] PowerPoint generated:")
    print(output_path)

    print("==============================")
    print("CODEVERSE PIPELINE COMPLETED")
    print("==============================\n")

    return {
        "transcript": transcript,
        "ai_result": ai_result,
        "pptx_filename": pptx_filename,
    }