from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    assistant_message: str
    emotion: str | None = None
    risk_level: str | None = None
    safety_bypassed: bool | None = None
    needs_exploration: bool | None = None
    latency_seconds: float | None = None
