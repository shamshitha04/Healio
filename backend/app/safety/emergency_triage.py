import re


EMERGENCY_TERMS = (
    "chest pain",
    "stroke",
    "severe bleeding",
    "unconscious",
    "trouble breathing",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "shortness of breath",
    "seizure",
    "poisoning",
    "suicidal thoughts",
    "severe allergic reaction",
    "anaphylaxis",
    "blue lips",
    "not breathing",
)


def detect_emergency(text: str) -> list[str]:
    normalized = text.lower()
    matches: list[str] = []

    for term in EMERGENCY_TERMS:
        pattern = r"\b" + re.escape(term).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            matches.append(term)

    return matches

