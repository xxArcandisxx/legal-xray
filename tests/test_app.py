import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app
from services import storage
from services.ai_service import validate_result


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATABASE", str(tmp_path / "test.db"))
    app.REQUESTS.clear()
    return app.app.test_client()


def test_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_sample_is_available_without_api_key(test_client):
    response = test_client.get(
        "/sample", headers={"X-Client-ID": "test-client-123"}
    )
    assert response.status_code == 200
    assert response.json["result"]["doc_type"] == "Rental agreement"


def test_history_is_scoped_to_client(test_client):
    test_client.get("/sample", headers={"X-Client-ID": "owner-123"})
    response = test_client.get("/history", headers={"X-Client-ID": "other-123"})
    assert response.status_code == 200
    assert response.json["items"] == []


def test_history_detail_does_not_include_original_text(test_client):
    sample = test_client.get("/sample", headers={"X-Client-ID": "owner-123"}).json
    response = test_client.get(
        f"/history/{sample['analysis_id']}", headers={"X-Client-ID": "owner-123"}
    )
    assert response.status_code == 200
    assert "text" not in response.json
    assert response.json["result"]["clauses"]


def test_validate_result_rejects_missing_translation():
    invalid = {
        "doc_type": "contract",
        "overall_risk": 40,
        "summary": {"en": "x", "hi": "x"},
        "clauses": [],
    }
    try:
        validate_result(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid result was accepted")
