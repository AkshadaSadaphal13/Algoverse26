from pathlib import Path

from faster_whisper import WhisperModel
from mutagen import File
from mutagen import MutagenError


# Whisper configuration for your laptop:
# Intel Core Ultra 5 125H + 16 GB RAM
WHISPER_MODEL_SIZE = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"


# Load the model only once.
_whisper_model = None


def get_audio_duration_seconds(file_path: Path) -> float:
    """
    Get the duration of an audio file in seconds.
    """

    try:
        audio = File(file_path)

    except MutagenError as exc:
        raise ValueError(
            "Unable to determine audio duration"
        ) from exc

    if (
        audio is None
        or not hasattr(audio, "info")
        or not getattr(audio.info, "length", None)
    ):
        raise ValueError(
            "Unable to determine audio duration"
        )

    return float(audio.info.length)


def get_whisper_model() -> WhisperModel:
    """
    Load the faster-whisper model once and reuse it.
    """

    global _whisper_model

    if _whisper_model is None:
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

    return _whisper_model


def transcribe_audio(file_path: Path) -> str:
    """
    Convert speech in an audio file into text using faster-whisper.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {file_path}"
        )

    model = get_whisper_model()

    segments, _ = model.transcribe(
        str(file_path),
        beam_size=5,
        vad_filter=True,
    )

    transcript_parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            transcript_parts.append(text)

    transcript = " ".join(transcript_parts).strip()

    if not transcript:
        raise ValueError(
            "No speech could be detected in the audio."
        )

    return transcript