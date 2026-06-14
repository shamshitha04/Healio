from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ScrubResult:
    text: str
    redacted: bool
    redaction_count: int


PII_PATTERNS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "[REDACTED_EMAIL]"),
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"), "[REDACTED_PHONE]"),
    (re.compile(r"\b(?:DOB|Date of Birth|born on)\s*[:\-]?\s*\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b", re.IGNORECASE), "[REDACTED_DOB]"),
    (re.compile(r"\b\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b"), "[REDACTED_DATE]"),
    (re.compile(r"\b(?:MRN|Medical Record|Patient ID|Record ID)\s*[:#-]?\s*[A-Z0-9-]{4,}\b", re.IGNORECASE), "[REDACTED_ID]"),
    (re.compile(r"\b(?i:my name is|patient name is|name is|i am|i'm|im|this is|patient:?|name:?)\s+[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3}\b"), "[REDACTED_NAME]"),
    (re.compile(r"\b\d{1,6}\s+[A-Z][A-Za-z0-9.\s]{1,40}\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b", re.IGNORECASE), "[REDACTED_ADDRESS]"),
    (re.compile(r"\b(?:I live in|from|located in)\s+[A-Z][A-Za-z.\s]+,\s*[A-Z]{2}\b", re.IGNORECASE), "[REDACTED_LOCATION]"),
)


def scrub_pii(text: str) -> ScrubResult:
    cleaned = text
    total = 0

    for pattern, replacement in PII_PATTERNS:
        cleaned, count = pattern.subn(replacement, cleaned)
        total += count

    return ScrubResult(text=cleaned, redacted=total > 0, redaction_count=total)

