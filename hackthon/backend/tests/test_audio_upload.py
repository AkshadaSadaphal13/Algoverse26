import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_audio_invalid_type():
    response = client.post(
        "/api/jobs/upload",
        files={"file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")},
    )
    assert response.status_code == 400
