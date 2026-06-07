# Healio Implementation Plan

## 1. PRD Analysis Summary

Healio is a privacy-first, child-friendly AI medical assistant. The core product is not only a chatbot; it is a safety-controlled medical support workflow where every user input must pass through local privacy and emergency checks before any cloud model call is allowed.

The application has four major responsibilities:

- Provide a warm, accessible, kid-friendly React interface for chat and medical document upload.
- Protect user privacy locally by redacting personally identifiable information before cloud inference.
- Detect emergency red flags locally and bypass the AI model entirely for urgent situations.
- Ground non-emergency answers using local medical reference material through RAG before calling Groq.

The most important implementation priority is the backend safety pipeline. The UI can be polished later, but the application should never send raw PII or emergency requests to the model.

## 2. Target Architecture

The project should be organized as:

```text
Healio/
  backend/
    app/
      main.py
      safety/
        pii_scrubber.py
        emergency_triage.py
      rag/
        ingest.py
        retriever.py
      ai/
        groq_client.py
        prompts.py
      models/
        schemas.py
    data/
      medical_guidelines/
      chroma/
    requirements.txt
    .env.example
  frontend/
    src/
      components/
      pages/
      services/
      App.jsx
      main.jsx
    package.json
    tailwind.config.js
  run_windows.bat
  run_mac_linux.sh
  README.md
  PRD.md
  Plan.md
```

This keeps safety, AI orchestration, RAG, and UI concerns separated so each part can be tested independently.

## 3. Build Phases

### Phase 1: Project Scaffold and Local Environment

Steps:

- Create `backend/` and `frontend/` directories.
- Initialize a Python virtual environment workflow for the backend.
- Add `backend/requirements.txt` with FastAPI, Uvicorn, Groq, LangChain, ChromaDB, Pydantic, python-dotenv, and file upload helpers.
- Scaffold React frontend with Vite.
- Install Tailwind CSS and configure the base theme.
- Add `.env.example` documenting `GROQ_API_KEY`.
- Create `run_windows.bat` and `run_mac_linux.sh` to start both backend and frontend.

Acceptance checks:

- Backend starts with `uvicorn app.main:app --reload`.
- Frontend starts with `npm run dev`.
- Root run scripts launch both services.
- README has basic local startup instructions.

### Phase 2: Backend API Foundation

Steps:

- Implement FastAPI app in `backend/app/main.py`.
- Add health endpoint: `GET /api/health`.
- Add chat endpoint: `POST /api/chat`.
- Define request and response schemas in `backend/app/models/schemas.py`.
- Add CORS configuration for the local frontend dev server.
- Return a temporary mock response before wiring Groq.

Acceptance checks:

- `/api/health` returns a simple healthy response.
- `/api/chat` accepts user text and returns a structured response.
- Frontend can call backend without CORS errors.

### Phase 3: Local Safety Layer

Steps:

- Create `pii_scrubber.py` with regex-based redaction for:
  - phone numbers
  - email addresses
  - dates of birth and date-like patterns
  - likely full-name phrases
  - addresses and location-like patterns where feasible
  - medical record or ID-like numbers
- Create `emergency_triage.py` with a configurable list of emergency keywords and phrases, including:
  - chest pain
  - stroke
  - severe bleeding
  - unconscious
  - trouble breathing
  - seizure
  - poisoning
  - suicidal thoughts
  - severe allergic reaction
- Ensure `/api/chat` runs triage before PII scrubbing and model routing.
- If emergency text is detected, return an emergency response object and do not call Groq or RAG.
- If no emergency is detected, scrub PII before any downstream processing.

Acceptance checks:

- Inputs containing emergency phrases return an urgent alert response immediately.
- Emergency inputs do not trigger model calls.
- Inputs with PII show redacted text in backend logs or test output.
- Raw PII is never passed to Groq or RAG.

### Phase 4: Groq and Prompt Orchestration

Steps:

- Create `groq_client.py` to wrap Groq API calls.
- Use model `openai/gpt-oss-120b` as required by the PRD.
- Create `prompts.py` with the enforced system prompt.
- Include prompt rules:
  - do not diagnose as a doctor
  - do not prescribe exact medication dosages
  - recommend professional medical care when appropriate
  - admit uncertainty when context is insufficient
  - include educational disclaimer in every non-emergency response
  - keep language friendly and understandable
- Add graceful handling for missing API keys and Groq API failures.

Acceptance checks:

- Normal health questions produce friendly, safe, disclaimer-bearing answers.
- Missing `GROQ_API_KEY` produces a clear local error, not a crash.
- Model failures return a user-safe fallback response.

### Phase 5: Local RAG Knowledge Base

Steps:

- Add `backend/data/medical_guidelines/` for source materials.
- Use 2-3 reputable open-source first-aid or general health guidance documents.
- Create `rag/ingest.py` to:
  - load source documents
  - split into chunks
  - generate embeddings
  - persist a local ChromaDB index in `backend/data/chroma/`
- Create `rag/retriever.py` to query the local ChromaDB index.
- Update `/api/chat` pipeline:
  - emergency triage
  - PII scrub
  - RAG similarity lookup
  - prompt assembly
  - Groq response
- Include retrieved context in prompt payload without exposing raw user PII.

Acceptance checks:

- Ingestion script creates a persistent ChromaDB store.
- Chat endpoint retrieves relevant chunks for health questions.
- The model references retrieved context indirectly and safely.
- If retrieval returns weak or empty results, the model is instructed to admit uncertainty.

### Phase 6: Medical Text and Report Upload

Steps:

- Add backend upload endpoint, likely `POST /api/upload`.
- Accept text files first; optionally support PDFs if dependencies allow.
- Extract text from the uploaded report.
- Run extracted text through the same safety pipeline:
  - emergency detection
  - PII scrubber
  - optional RAG context
  - Groq summarization
- Return a plain-language summary with disclaimers.

Acceptance checks:

- Upload zone can send a file to the backend.
- PII in uploaded medical text is redacted before model use.
- Emergency content in uploaded reports triggers an alert.
- Summary is understandable and clearly not a medical diagnosis.

### Phase 7: Frontend Experience

Steps:

- Configure Tailwind with the "Soft Clinic" palette:
  - warm off-white or cream background
  - mint and baby-blue accents
  - peach/coral primary actions
  - warm orange-red emergency alerts
- Apply rounded, readable typography such as Nunito or Quicksand.
- Build main layout:
  - header with Healio name and mascot/avatar
  - central chat interface
  - friendly rulebook sidebar
  - symptom bubble row
  - upload zone
- Implement chat state:
  - user messages
  - assistant messages
  - loading state
  - emergency alert state
  - error state
- Implement symptom bubbles that send or prefill common prompts.
- Implement drag-and-drop upload UI.

Acceptance checks:

- UI is responsive on mobile and desktop.
- Text remains readable and does not overlap.
- Emergency responses are visually distinct.
- The first screen feels like the usable app, not a marketing landing page.

### Phase 8: End-to-End Integration

Steps:

- Connect frontend chat service to `POST /api/chat`.
- Connect upload zone to `POST /api/upload`.
- Normalize backend response types so the frontend can render:
  - normal assistant answer
  - emergency alert
  - upload summary
  - backend error
- Add user-facing loading and retry states.
- Verify both run scripts start the full application.

Acceptance checks:

- User can ask a normal health question and receive a response.
- User can click symptom bubbles and receive responses.
- User can upload a medical text/report and receive a summary.
- Emergency phrases bypass normal chat and render an alert card.

### Phase 9: Testing

Backend tests:

- PII scrubber redacts expected sensitive patterns.
- Emergency detector catches red-flag phrases.
- Emergency route bypasses Groq.
- Chat route sends only scrubbed text downstream.
- RAG retriever handles empty index or no-match cases.

Frontend tests or manual QA:

- Chat submission works.
- Loading and error states render.
- Symptom bubbles work.
- Upload zone handles valid and invalid files.
- Mobile layout remains usable.

Manual safety test prompts:

- "My name is John Smith, my phone is 555-123-4567, and my head hurts."
- "I have chest pain and trouble breathing."
- "Summarize this report for a child."
- "How much medicine should I take?"
- "Who won the football game yesterday?"

Acceptance checks:

- PII is redacted.
- Emergency prompts never call Groq.
- Medication dosage requests are refused or redirected safely.
- Out-of-scope prompts receive a graceful refusal.

### Phase 10: Documentation and Submission Package

Steps:

- Write `README.md` with:
  - product overview
  - architecture summary
  - local-first privacy explanation
  - emergency triage explanation
  - setup instructions for Windows and macOS/Linux
  - environment variable setup
  - testing scenarios
- Add clear notes that Healio is educational and not a replacement for medical care.
- Prepare contest demo script:
  - show startup
  - show friendly UI
  - show PII redaction
  - show emergency bypass
  - show RAG-backed response
  - show report upload summary

Acceptance checks:

- Evaluator can run the app from a clean checkout.
- Demo flow proves the safety-first architecture.
- Documentation explains why local-first preprocessing matters.

## 4. Backend Request Pipeline

The chat endpoint should follow this exact order:

```text
Receive user input
  -> emergency triage
    -> if emergency: return emergency alert, bypass all AI calls
  -> PII scrubber
  -> RAG retrieval using scrubbed input
  -> prompt assembly with system prompt, scrubbed input, and retrieved context
  -> Groq model call
  -> response post-processing
  -> return structured response to frontend
```

This order is critical. Emergency handling must happen before any model call, and PII scrubbing must happen before any cloud request.

## 5. Suggested API Contract

### `POST /api/chat`

Request:

```json
{
  "message": "My head hurts and I feel hot"
}
```

Normal response:

```json
{
  "type": "answer",
  "message": "Friendly assistant response with educational disclaimer.",
  "redacted": false,
  "sources_used": true
}
```

Emergency response:

```json
{
  "type": "emergency",
  "message": "This may be urgent. Please stop using this app and contact local emergency services immediately.",
  "matched_terms": ["chest pain"]
}
```

### `POST /api/upload`

Request:

```text
multipart/form-data with file
```

Response:

```json
{
  "type": "summary",
  "message": "Plain-language summary of the uploaded medical text.",
  "redacted": true
}
```

## 6. Key Risks and Mitigations

- Medical safety risk: mitigate with emergency bypass, conservative system prompt, disclaimers, and refusal for exact dosing.
- Privacy risk: mitigate by placing PII scrubber before RAG and Groq calls.
- RAG quality risk: use reputable source documents and instruct the model to admit uncertainty when retrieved context is weak.
- Setup risk: avoid Docker as required, provide simple scripts and `.env.example`.
- API availability risk: provide graceful fallback when Groq is unavailable or the API key is missing.
- UI trust risk: keep design friendly but avoid implying the assistant is a real doctor.

## 7. Recommended Implementation Order

1. Scaffold backend and frontend.
2. Implement backend health and chat endpoints.
3. Implement emergency triage.
4. Implement PII scrubber.
5. Add Groq wrapper and enforced prompt.
6. Add RAG ingestion and retrieval.
7. Build chat UI, sidebar, mascot header, and symptom bubbles.
8. Add report upload endpoint and frontend upload zone.
9. Integrate all frontend/backend flows.
10. Add tests and README.
11. Run full manual demo scenarios.

## 8. Definition of Done

The application is complete when:

- A user can run the app locally without Docker.
- The UI is responsive, friendly, and usable as the first screen.
- Chat works through the backend API.
- Uploaded medical text can be summarized.
- Emergency red flags return immediate alert responses and bypass AI calls.
- PII is redacted before any cloud model request.
- RAG context is loaded from local medical reference material.
- Every non-emergency answer includes an educational medical disclaimer.
- README explains setup, safety behavior, and demo scenarios.
- Core safety functions have tests or documented manual verification.
