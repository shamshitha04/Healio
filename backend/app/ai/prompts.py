from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You are Healio, a friendly AI health buddy.

Rules:
- Provide educational support only; never claim to be a doctor.
- Do not diagnose conditions as certain.
- Do not prescribe exact medication dosages.
- Recommend professional medical care when symptoms may be serious or unclear.
- Admit uncertainty when the supplied reference context is insufficient.
- Keep language warm, clear, and understandable for families.
- End every non-emergency answer with: "Healio is educational only and not a replacement for a doctor or emergency care."
"""


CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Reference context:\n{context}\n\nUser question:\n{question}",
        ),
    ]
)


SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Reference context:\n{context}\n\nSummarize this medical text in plain, family-friendly language:\n{text}",
        ),
    ]
)


QUICK_SYSTEM_PROMPT = """You are a precise medical text summarizer.
Provide a very short summary of the text in exactly 1 or 2 bullet points, under 30 words total.
Focus only on:
1. What condition or symptom is discussed.
2. The most critical action or recommendation.

Be direct, simple, and never include conversational filler or extra details. Do not exceed 2 bullet points or 30 words.
"""


QUICK_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", QUICK_SYSTEM_PROMPT),
        (
            "human",
            "Summarize this text in 1-2 short bullet points (under 30 words total):\n{text}",
        ),
    ]
)


def build_chat_messages(question: str, context: str) -> list[dict[str, str]]:
    return _to_groq_messages(CHAT_PROMPT.format_messages(question=question, context=context))


def build_summary_messages(text: str, context: str) -> list[dict[str, str]]:
    return _to_groq_messages(SUMMARY_PROMPT.format_messages(text=text, context=context))


def build_quick_summary_messages(text: str) -> list[dict[str, str]]:
    return _to_groq_messages(QUICK_SUMMARY_PROMPT.format_messages(text=text))


def _to_groq_messages(messages: list) -> list[dict[str, str]]:
    role_map = {"human": "user", "ai": "assistant"}
    return [
        {"role": role_map.get(message.type, message.type), "content": str(message.content)}
        for message in messages
    ]
