import os
import secrets
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile


ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str, content_type: str) -> bool:
    ext = get_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        return False

    allowed_content_types = {
        "mp3": {
            "audio/mpeg",
            "audio/mp3",
        },
        "wav": {
            "audio/wav",
            "audio/x-wav",
            "audio/wave",
            "audio/vnd.wave",
        },
        "m4a": {
            "audio/mp4",
            "audio/x-m4a",
            "audio/m4a",
            "application/mp4",
            "application/octet-stream",
        },
    }

    return content_type.lower() in allowed_content_types.get(ext, set())


def secure_filename(original_filename: str) -> str:
    ext = get_extension(original_filename)
    token = secrets.token_hex(16)
    return f"{token}.{ext}" if ext else token


def save_upload(upload_file: UploadFile, destination: Path) -> Tuple[str, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)

    data = upload_file.file.read()

    if len(data) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    destination.write_bytes(data)

    return str(destination), len(data)