from app.safety import detect_emergency, scrub_pii
from app.ai.groq_client import generate_medical_response
import app.ai.groq_client as groq_client
from app.ai.prompts import build_chat_messages
from app.rag.retriever import retrieve_context


def test_detect_emergency_terms():
    matches = detect_emergency("The patient has severe bleeding and may be unconscious.")
    assert "severe bleeding" in matches
    assert "unconscious" in matches


def test_scrub_pii_patterns():
    result = scrub_pii(
        "My name is Jane Smith. Email jane@example.com. DOB: 01/02/2000. "
        "Phone 555-123-4567. Patient ID: HX12345."
    )

    assert result.redacted is True
    assert "jane@example.com" not in result.text
    assert "555-123-4567" not in result.text
    assert "01/02/2000" not in result.text
    assert "HX12345" not in result.text


def test_prompt_messages_use_groq_roles():
    roles = [message["role"] for message in build_chat_messages("My head hurts.", "")]

    assert roles == ["system", "user"]


def test_dosage_question_gets_safe_local_response(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = generate_medical_response("How much medicine should I take?", "")

    assert "cannot tell you exactly how much medicine to take" in response
    assert "educational only" in response


def test_out_of_scope_question_gets_graceful_refusal(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = generate_medical_response("Who won the football game yesterday?", "")

    assert "only help with general health education" in response


def test_placeholder_groq_key_uses_safe_fallback(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "your_groq_api_key_here")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Placeholder API key should not call Groq")

    monkeypatch.setattr(groq_client, "Groq", fail_if_called)

    response = generate_medical_response("My head hurts.", "")

    assert "cannot diagnose" in response
    assert "educational only" in response


def test_retriever_handles_empty_query():
    context = retrieve_context("")

    assert isinstance(context, str)
