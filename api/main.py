from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.firestore_service import ensure_session, save_message
from api.schemas import ChatRequest, ChatResponse
from agents.coordinator.coordinator import Coordinator


app = FastAPI(title="Atapia API")
coordinator = Coordinator()


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid4())

    try:
        ensure_session(session_id)
        save_message(
            session_id=session_id,
            role="user",
            content=request.message,
        )
    except Exception as exc:
        print(f"Firestore user message save failed: {exc}")

    try:
        response = coordinator.handle_message(
            user_message=request.message,
            user_id=session_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message.",
        ) from exc

    chat_response = ChatResponse(
        session_id=session_id,
        assistant_message=getattr(response, "assistant_message", ""),
        emotion=getattr(response, "emotion", None),
        risk_level=getattr(response, "risk_level", None),
        safety_bypassed=getattr(response, "safety_bypassed", None),
        needs_exploration=getattr(response, "needs_exploration", None),
    )

    try:
        save_message(
            session_id=session_id,
            role="assistant",
            content=chat_response.assistant_message or "",
            metadata={
                "emotion": chat_response.emotion,
                "risk_level": chat_response.risk_level,
                "safety_bypassed": chat_response.safety_bypassed,
                "needs_exploration": chat_response.needs_exploration,
            },
        )
    except Exception as exc:
        print(f"Firestore assistant message save failed: {exc}")

    return chat_response
