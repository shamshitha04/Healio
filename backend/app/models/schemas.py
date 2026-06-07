from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    type: Literal["answer"] = "answer"
    message: str
    redacted: bool = False
    sources_used: bool = False


class EmergencyResponse(BaseModel):
    type: Literal["emergency"] = "emergency"
    message: str
    matched_terms: list[str]


class UploadResponse(BaseModel):
    type: Literal["summary"] = "summary"
    message: str
    redacted: bool = False
    sources_used: bool = False
