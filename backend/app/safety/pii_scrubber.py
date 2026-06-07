from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ScrubResult:
    text: str
    redacted: bool
    redaction_count: int


PII_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[REDACTED_EMAIL]"),
    (r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    (r"\b(?:DOB|Date of Birth|born on)\s*[:\-]?\s*\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b", "[REDACTED_DOB]"),
    (r"\b\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b", "[REDACTED_DATE]"),
    (r"\b(?:MRN|Medical Record|Patient ID|Record ID)\s*[:#-]?\s*[A-Z0-9-]{4,}\b", "[REDACTED_ID]"),
    (r"\b(?:my name is|patient name is|name is)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b", "[REDACTED_NAME]"),
    (r"\b\d{1,6}\s+[A-Z][A-Za-z0-9.\s]{1,40}\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b", "[REDACTED_ADDRESS]"),
    (r"\b(?:I live in|from|located in)\s+[A-Z][A-Za-z.\s]+,\s*[A-Z]{2}\b", "[REDACTED_LOCATION]"),
)


def scrub_pii(text: str) -> ScrubResult:
    cleaned = text
    total = 0

    for pattern, replacement in PII_PATTERNS:
        cleaned, count = re.subn(pattern, replacement, cleaned, flags=re.IGNORECASE)
        total += count

    return ScrubResult(text=cleaned, redacted=total > 0, redaction_count=total)

