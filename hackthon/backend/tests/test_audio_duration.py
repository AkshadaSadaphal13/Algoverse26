from pathlib import Path
import pytest

from app.services.audio_service import get_audio_duration_seconds


def test_audio_duration_invalid_file(tmp_path: Path):
    invalid_audio = tmp_path / "invalid.mp3"
    invalid_audio.write_bytes(b"not audio data")

    with pytest.raises(ValueError, match="Unable to determine audio duration"):
        get_audio_duration_seconds(invalid_audio)
