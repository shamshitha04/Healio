from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader

from app.ai.groq_client import extract_text_from_image


MAX_UPLOAD_BYTES = 2 * 1024 * 1024
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


async def extract_upload_text(file: UploadFile) -> str:
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file is too large. Please upload a file under 2 MB.")

    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()

    if filename.endswith(".pdf") or content_type == "application/pdf":
        return _extract_pdf_text(content)

    if filename.endswith((".txt", ".md", ".csv")) or content_type.startswith("text/"):
        return content.decode("utf-8", errors="replace")

    if filename.endswith(IMAGE_EXTENSIONS) or content_type in IMAGE_CONTENT_TYPES:
        image_content_type = content_type if content_type in IMAGE_CONTENT_TYPES else _image_content_type(filename)
        text = extract_text_from_image(content, image_content_type)
        if text:
            return text
        raise ValueError(
            "Healio could not read text from that image. Please upload a clearer image or type the report text."
        )

    raise ValueError("Unsupported file type. Please upload a .txt, .md, .csv, .pdf, .jpg, .png, or .webp file.")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _image_content_type(filename: str) -> str:
    if filename.endswith(".png"):
        return "image/png"
    if filename.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"
