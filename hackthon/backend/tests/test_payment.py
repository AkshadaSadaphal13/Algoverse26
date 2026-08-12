import io
import wave

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_silent_wav(duration_seconds: int = 1, sample_rate: int = 44100) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * sample_rate * duration_seconds)
    buffer.seek(0)
    return buffer.read()


def test_payment_required_for_unverified_job():
    response = client.post("/api/jobs/unknown-job/process")
    assert response.status_code == 404


def test_process_requires_payment_for_new_job():
    audio_data = create_silent_wav()
    response = client.post(
        "/api/jobs/upload",
        files={"file": ("test.wav", audio_data, "audio/wav")},
    )
    assert response.status_code == 200

    job_id = response.json()["job_id"]
    process_response = client.post(f"/api/jobs/{job_id}/process")
    assert process_response.status_code == 402


def test_payment_api_creates_payment_record():
    audio_data = create_silent_wav()
    response = client.post(
        "/api/jobs/upload",
        files={"file": ("test.wav", audio_data, "audio/wav")},
    )
    assert response.status_code == 200

    job_id = response.json()["job_id"]
    payment_response = client.get(f"/api/jobs/{job_id}/payment")
    assert payment_response.status_code == 200
    assert payment_response.json()["payment_status"] == "pending"


def test_verify_payment_and_process_job():
    audio_data = create_silent_wav()
    response = client.post(
        "/api/jobs/upload",
        files={"file": ("test.wav", audio_data, "audio/wav")},
    )
    assert response.status_code == 200

    job_id = response.json()["job_id"]
    verify_response = client.post(
        f"/api/jobs/{job_id}/payment/verify",
        json={"transaction_id": "SIMULATED_TX_123", "payer_wallet": "SIMULATED_WALLET_ABC"},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["payment_status"] == "verified"

    process_response = client.post(f"/api/jobs/{job_id}/process")
    assert process_response.status_code == 200
    result_data = process_response.json()
    assert result_data["processing_status"] == "completed"
    assert result_data["payment_status"] == "verified"
    assert result_data["result_summary"] is not None
