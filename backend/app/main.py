import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.ai.groq_client import generate_medical_response, generate_medical_summary
from app.models import ChatRequest, ChatResponse, EmergencyResponse, HealthResponse, UploadResponse
from app.rag import retrieve_context
from app.safety import detect_emergency, scrub_pii
from app.uploads import extract_upload_text


load_dotenv()


app = FastAPI(
    title="Healio API",
    description="Privacy-first, child-friendly medical assistant backend.",
    version="0.1.0",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="healio-api")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse | EmergencyResponse:
    cleaned_message = request.message.strip()
    emergency_terms = detect_emergency(cleaned_message)
    if emergency_terms:
        return _emergency_response(emergency_terms)

    scrubbed = scrub_pii(cleaned_message)
    context = retrieve_context(scrubbed.text)
    answer = generate_medical_response(scrubbed.text, context)

    return ChatResponse(message=answer, redacted=scrubbed.redacted, sources_used=bool(context))


@app.post("/api/upload")
async def upload_report(file: UploadFile = File(...)) -> UploadResponse | EmergencyResponse:
    try:
        text = (await extract_upload_text(file)).strip()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text:
        raise HTTPException(status_code=400, detail="Uploaded file did not contain readable text.")

    emergency_terms = detect_emergency(text)
    if emergency_terms:
        return _emergency_response(emergency_terms)

    scrubbed = scrub_pii(text)
    context = retrieve_context(scrubbed.text)
    summary = generate_medical_summary(scrubbed.text, context)

    return UploadResponse(message=summary, redacted=scrubbed.redacted, sources_used=bool(context))


def _emergency_response(matched_terms: list[str]) -> EmergencyResponse:
    return EmergencyResponse(
        message=(
            "This may be urgent. Please stop using this app and contact local "
            "emergency services immediately. If you are in the United States, "
            "call 911 now."
        ),
        matched_terms=matched_terms,
    )
