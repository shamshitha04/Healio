📝 Product Requirements Document (PRD)
Project Name: Healio – The Friendly AI Medical Assistant

Contest: AI Model Development Contest

Primary Goal: Develop a responsive, privacy-first, and child-friendly medical assistant bot named Healio that answers health queries and summarizes medical text. The system prioritizes patient safety by using a local-first PII scrubber and an emergency red-flag detector before routing anonymized data to the ultra-fast Groq API (openai/gpt-oss-120b).

1. Core Architecture & Tech Stack
Healio uses a clean decoupled architecture optimized for rapid local setup by evaluators without containerization overhead.

Frontend (UI/UX): React, Tailwind CSS (configured for a soft, approachable aesthetic).

Backend (API & Logic): Python, FastAPI (asynchronous, lightweight framework).

AI Orchestration: LangChain (for prompt construction and context injection).

Cloud Inference: Groq API running openai/gpt-oss-120b (Free Tier).

Vector Database: ChromaDB (Local, embedded persistent storage).

Deployment Strategy: Native Python Virtual Environment (venv) with custom batch/shell scripts for a seamless, one-click evaluation experience. No Docker dependency.

2. UI/UX Specifications: The "Friendly Companion"
Healio is built to look like a comforting health companion rather than a sterile clinical application, making it easy and engaging for users of all ages, including children.

Visual Identity & Theme
Color Palette ("Soft Clinic"):

Background: Soft cream (bg-amber-50) or warm off-white.

Primary Accents: Mint green (bg-emerald-200) and baby blue (bg-sky-200) for a gentle medical feel.

Call-to-Action / Primary Buttons: Soft peach/coral (bg-rose-300).

Alerts / Red Flags: Warm orange-red (bg-red-400) instead of aggressive neon red.

Typography: Soft, rounded, highly readable fonts (e.g., Nunito or Quicksand) applied globally with enlarged text sizing (text-lg) for extreme readability.

Mascot Persona: A friendly, animated avatar of Healio (a smiling robot helper) greets the user with an inviting message: "Hi! I'm Healio, your friendly health buddy. Where does it hurt today?"

Key Interface Components
Symptom Bubbles: A quick-click row of pill-shaped buttons under the chat interface representing common kid-friendly complaints (e.g., "🤕 My head hurts", "🤒 I feel hot", "🤧 I am sneezing") to minimize typing friction.

Gamified Upload Zone: A prominent, soft-shadowed drag-and-drop zone with a happy "+" icon for dropping medical reports, styled like a mini-game.

The Friendly "Rulebook" Sidebar: A simplified, colorful side panel that frames the required legal disclaimers and privacy notices in warm language: "🤖 Healio's Golden Rule: I am a super-smart AI, but I'm not a real human doctor! Always show my answers to a grown-up or doctor to be safe."

3. Feature Requirements & Safety Pipelines
3.1 Local-First Privacy Layer (The Scrubber)
Requirement: Ensure absolute data privacy before sending any prompt or text chunk to a cloud endpoint.

Implementation: A dedicated local Python module (pii_scrubber.py) uses fast Regular Expressions to intercept user inputs and redact Personally Identifiable Information (PII) such as full names, dates of birth, phone numbers, and location details, replacing them with [REDACTED].

3.2 Emergency Red-Flag Triage
Requirement: Prevent the AI from handling or misdiagnosing life-threatening conditions.

Implementation: A hardcoded interceptor scans text inputs for critical emergency keywords (e.g., stroke, chest pain, severe bleeding, unconscious). If an emergency is triggered, the backend completely bypasses the Groq API call and returns an explicit, high-priority orange-red alert card telling the user to stop using the app and contact local emergency services immediately.

3.3 Medical Knowledge Retrieval (RAG)
Requirement: Ground the model in verified medical guidelines to mitigate hallucinations.

Implementation: Integrate LangChain to read, chunk, and embed 2-3 open-source first-aid or medical guidelines into a local ChromaDB instance stored inside the backend directory. The system queries this local index dynamically to append reliable context directly into the prompt payload.

3.4 Enforced System Prompt
Requirement: Keep the gpt-oss-120b reasoning engine strictly restricted to its supportive role.

Implementation: The background payload contains strict instructions: never prescribe exact medication dosages, admit uncertainty transparently if the RAG context is insufficient, and append the necessary educational disclaimer to every non-emergency response.

4. Step-by-Step Implementation Roadmap
Phase 1: Native Environment Setup
Create a root project folder with isolated frontend/ and backend/ directories.

Initialize the backend Python virtual environment (venv) and set up a standard requirements.txt listing fastapi, uvicorn, groq, langchain, and chromadb.

Scaffold the frontend using React and initialize Tailwind CSS.

Write a root-level run_windows.bat script and a run_mac_linux.sh script to launch both servers simultaneously with a single execution step.

Phase 2: Core Safety Backend
Build the local pii_scrubber.py component to handle automated string cleaning.

Implement the emergency keyword interceptor function.

Configure the main FastAPI endpoint (/api/chat) to sequentially execute the interceptor, run the scrubber, and route the scrubbed data safely to the Groq client.

Phase 3: Embedded RAG Database
Place standard medical or first-aid reference text/PDFs into a local backend data folder.

Construct a script to ingest these materials, generate structural embeddings, and save them natively in a persistent local ChromaDB directory.

Update the /api/chat pipeline to perform a similarity lookup right after scrubbing data, injecting the retrieved text chunks as reference material for the model.

Phase 4: Accessible Interface Development
Configure tailwind.config.js with the custom "Soft Clinic" pastel color palette.

Build out the persistent layout structure including the Sidebar ("Rulebook"), the Header featuring the Healio mascot, and the central Chat field.

Implement the interactive "Symptom Bubbles" and the drag-and-drop document upload interface.

Phase 5: Testing & Presentation Package
Testing Scenarios: Input mock clinical records to verify PII masking, submit critical emergency words to ensure immediate warning bypass, and issue out-of-scope questions to check the bot's graceful refusal mechanism.

Documentation: Write a detailed README.md focusing on the local-first security stance and simple terminal start steps.

Submission Video: Record the project walkthrough demonstrating smooth chat messaging, text report processing, and the visual design execution.