# Healio

Healio is a privacy-first, child-friendly AI medical assistant for local demos. It provides a warm chat interface and medical report upload flow while keeping the highest-risk safety checks on the local machine before any cloud model request is allowed.

Healio is educational only. It is not a doctor, cannot diagnose, and must not be used instead of emergency care.

## What It Does

- Accepts general health questions through a React chat UI.
- Accepts `.txt`, `.md`, `.csv`, and `.pdf` medical report uploads under 2 MB.
- Detects emergency red flags locally and returns an urgent alert without calling AI or RAG.
- Redacts likely PII locally before retrieval or Groq requests.
- Retrieves local first-aid and medication-safety context from a Chroma knowledge base.
- Uses Groq with `openai/gpt-oss-120b` when `GROQ_API_KEY` is configured.
- Falls back to conservative local responses when the Groq key is missing or the API fails.

## Architecture

```text
Healio/
  backend/
    app/
      main.py                 FastAPI routes and safety pipeline
      safety/                 Emergency triage and PII scrubbing
      rag/                    Local guideline ingestion and retrieval
      ai/                     Groq client and medical prompts
      models/                 API schemas
    data/
      medical_guidelines/     Local reference text
      chroma/                 Persisted local vector store
    tests/                    Backend safety and API tests
  frontend/
    src/App.jsx               Main React experience
  run_windows.bat             Windows startup helper
  run_mac_linux.sh            macOS/Linux startup helper
```

The chat and upload routes both use this order:

```text
Receive input
  -> emergency triage
  -> if emergency: return alert and bypass AI/RAG
  -> PII scrubber
  -> local RAG retrieval with scrubbed text
  -> Groq prompt assembly and completion
  -> safe fallback if Groq is unavailable
```

## Setup

Create `backend/.env` from `backend/.env.example`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
FRONTEND_ORIGIN=http://localhost:5173
```

The app still runs without a Groq key, but responses use conservative local fallbacks.

## Run Locally

On Windows:

```bat
run_windows.bat
```

On macOS/Linux:

```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

Manual startup:

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

## Test

Backend:

```bash
cd backend
.venv/Scripts/python -m pytest tests
```

From the project root:

```bash
backend/.venv/Scripts/python -m pytest
```

Frontend build:

```bash
cd frontend
npm run build
```

## Demo Script

1. Start the backend and frontend.
2. Open `http://localhost:5173`.
3. Ask: `My name is John Smith, my phone is 555-123-4567, and my head hurts.`
   - Expected: normal answer, PII redaction badge, no raw phone number in the answer.
4. Ask: `I have chest pain and trouble breathing.`
   - Expected: emergency alert, matched emergency terms, AI/RAG bypass.
5. Ask: `How much medicine should I take?`
   - Expected: refusal to give exact dosage and recommendation to follow label or clinician guidance.
6. Upload a small text report.
   - Expected: plain-language summary, same emergency and PII protections.
7. Ask: `Who won the football game yesterday?`
   - Expected: graceful refusal because Healio only handles health education and report summaries.

## Safety Notes

Emergency detection runs before PII redaction and before any downstream system. If a red-flag phrase is found, Healio returns an emergency response and does not call Groq or RAG.

PII scrubbing is regex-based and intended for demo safety, not a compliance guarantee. The app redacts common phone numbers, email addresses, date-like values, likely name phrases, addresses, and ID-like values before retrieval or model calls.

The local RAG knowledge base uses compact reference summaries for demo purposes. It helps ground responses, but it is not a full medical corpus.
