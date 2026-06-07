from fastapi.testclient import TestClient

import app.main as main_module
import app.uploads as uploads_module
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "healio-api"}


def test_chat_redacts_pii_before_answer():
    response = client.post(
        "/api/chat",
        json={"message": "My name is John Smith, my phone is 555-123-4567, and my head hurts."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "answer"
    assert body["redacted"] is True
    assert "555-123-4567" not in body["message"]


def test_chat_emergency_bypasses_answer_pipeline():
    response = client.post("/api/chat", json={"message": "I have chest pain and trouble breathing."})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "emergency"
    assert "chest pain" in body["matched_terms"]


def test_chat_sends_only_scrubbed_text_downstream(monkeypatch):
    observed = {}

    def fake_retrieve_context(query):
        observed["rag_query"] = query
        return "first aid context"

    def fake_generate_medical_response(question, context):
        observed["model_question"] = question
        observed["model_context"] = context
        return "safe answer"

    monkeypatch.setattr(main_module, "retrieve_context", fake_retrieve_context)
    monkeypatch.setattr(main_module, "generate_medical_response", fake_generate_medical_response)

    response = client.post(
        "/api/chat",
        json={"message": "My name is John Smith and my email is john@example.com. My head hurts."},
    )

    assert response.status_code == 200
    assert response.json()["redacted"] is True
    assert "John Smith" not in observed["rag_query"]
    assert "john@example.com" not in observed["rag_query"]
    assert observed["rag_query"] == observed["model_question"]
    assert observed["model_context"] == "first aid context"


def test_chat_emergency_never_calls_downstream(monkeypatch):
    def fail_retrieve_context(query):
        raise AssertionError("RAG should not run for emergency messages")

    def fail_generate_medical_response(question, context):
        raise AssertionError("Groq should not run for emergency messages")

    monkeypatch.setattr(main_module, "retrieve_context", fail_retrieve_context)
    monkeypatch.setattr(main_module, "generate_medical_response", fail_generate_medical_response)

    response = client.post("/api/chat", json={"message": "I have chest pain."})

    assert response.status_code == 200
    assert response.json()["type"] == "emergency"


def test_upload_text_summary_redacts_pii():
    response = client.post(
        "/api/upload",
        files={"file": ("report.txt", "Patient ID: ABC12345\nPhone 555-123-4567\nMild cough.", "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "summary"
    assert body["redacted"] is True
    assert "555-123-4567" not in body["message"]


def test_upload_emergency_returns_alert():
    response = client.post(
        "/api/upload",
        files={"file": ("report.txt", "Patient is unconscious after a fall.", "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "emergency"
    assert "unconscious" in body["matched_terms"]


def test_upload_image_summary_uses_extracted_text(monkeypatch):
    monkeypatch.setattr(
        uploads_module,
        "extract_text_from_image",
        lambda content, content_type: "Patient ID: ABC12345\nPhone 555-123-4567\nMild cough.",
    )

    response = client.post(
        "/api/upload",
        files={"file": ("report.png", b"fake image bytes", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "summary"
    assert body["redacted"] is True
    assert "555-123-4567" not in body["message"]
