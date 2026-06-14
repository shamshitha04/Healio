import os
from base64 import b64encode

from groq import Groq

from app.ai.prompts import build_chat_messages, build_summary_messages, build_quick_summary_messages


DISCLAIMER = "Healio is educational only and not a replacement for a doctor or emergency care."


def generate_medical_response(question: str, context: str) -> str:
    if _asks_for_exact_dosage(question):
        return (
            "I cannot tell you exactly how much medicine to take. Medicine doses depend on age, "
            "weight, health history, the exact product, and other medicines. Please follow the "
            "label or a clinician's instructions, and contact a pharmacist or doctor if you are "
            f"unsure. {DISCLAIMER}"
        )

    if _is_out_of_scope(question):
        return (
            "I can only help with general health education and medical text summaries. "
            "For sports, news, homework, or other topics, please use a different trusted source. "
            f"{DISCLAIMER}"
        )

    messages = build_chat_messages(question=question, context=context)
    return _complete(messages, fallback=_fallback_answer(question, context))


def generate_medical_summary(text: str, context: str) -> str:
    messages = build_summary_messages(text=text, context=context)
    return _complete(messages, fallback=_fallback_summary(text, context))


def generate_quick_summary(text: str) -> str:
    messages = build_quick_summary_messages(text=text)
    fallback = (
        "Potential symptoms/conditions discussed. Please consult a clinician "
        f"for proper evaluation and diagnosis. {DISCLAIMER}"
    )
    return _complete(messages, fallback=fallback)


def extract_text_from_image(content: bytes, content_type: str) -> str:
    api_key = _configured_api_key()
    if not api_key:
        return ""

    image_url = f"data:{content_type};base64,{b64encode(content).decode('ascii')}"
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract only the readable medical text from this image. "
                            "If there is no readable text, return an empty response."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0,
        max_tokens=900,
    )
    return (completion.choices[0].message.content or "").strip()


def _complete(messages: list[dict[str, str]], fallback: str) -> str:
    api_key = _configured_api_key()
    if not api_key:
        return fallback

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=messages,
            temperature=0.2,
            max_tokens=700,
        )
        content = completion.choices[0].message.content or fallback
    except Exception:
        return fallback

    if DISCLAIMER not in content:
        content = f"{content.rstrip()}\n\n{DISCLAIMER}"
    return content


def _configured_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    placeholder_values = {"", "your_groq_api_key_here", "your_api_key_here"}
    if api_key.lower() in placeholder_values:
        return ""
    return api_key


def _fallback_answer(question: str, context: str) -> str:
    context_note = _context_note(context)
    return (
        "I can share general health education, but I cannot diagnose you. "
        f"{context_note} For symptoms that are severe, worsening, unusual, or worrying, "
        f"please contact a doctor or local urgent care. {DISCLAIMER}"
    )


def _fallback_summary(text: str, context: str) -> str:
    short_text = " ".join(text.split())[:500]
    context_note = _context_note(context)
    return (
        "Here is a plain-language summary based on the uploaded text: "
        f"{short_text or 'No readable medical text was found.'} "
        f"{context_note} Please review this with a qualified clinician. {DISCLAIMER}"
    )


def _context_note(context: str) -> str:
    if context.strip():
        return "I found some related first-aid reference context, so I will stay conservative."
    return "I do not have enough reference context for a confident answer."


def _asks_for_exact_dosage(question: str) -> bool:
    normalized = question.lower()
    dosage_words = ("dose", "dosage", "how much", "how many", "mg", "milligram", "teaspoon")
    medicine_words = ("medicine", "medication", "pill", "tablet", "ibuprofen", "acetaminophen", "paracetamol")
    return any(word in normalized for word in dosage_words) and any(
        word in normalized for word in medicine_words
    )


def _is_out_of_scope(question: str) -> bool:
    normalized = question.lower()
    out_of_scope_terms = (
        "football game",
        "basketball game",
        "soccer game",
        "stock price",
        "weather tomorrow",
        "movie recommendation",
    )
    health_terms = (
        "pain",
        "hurt",
        "fever",
        "cough",
        "rash",
        "symptom",
        "medicine",
        "doctor",
        "injury",
        "allergy",
        "report",
        "lab",
    )
    return any(term in normalized for term in out_of_scope_terms) and not any(
        term in normalized for term in health_terms
    )
