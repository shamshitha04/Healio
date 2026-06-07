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


def build_chat_messages(question: str, context: str) -> list[dict[str, str]]:
    return _to_groq_messages(CHAT_PROMPT.format_messages(question=question, context=context))


def build_summary_messages(text: str, context: str) -> list[dict[str, str]]:
    return _to_groq_messages(SUMMARY_PROMPT.format_messages(text=text, context=context))


def _to_groq_messages(messages: list) -> list[dict[str, str]]:
    role_map = {"human": "user", "ai": "assistant"}
    return [
        {"role": role_map.get(message.type, message.type), "content": str(message.content)}
        for message in messages
    ]
