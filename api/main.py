from __future__ import annotations

import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.firestore_service import ensure_session, save_message
from api.schemas import ChatRequest, ChatResponse
from agents.coordinator.coordinator import Coordinator


logger = logging.getLogger("uvicorn.error")
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Atapia API")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

coordinator = Coordinator()


class HealthResponse(BaseModel):
    status: str


@app.get("/")
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


def save_message_background(
    session_id: str,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> None:
    firestore_start = time.perf_counter()

    try:
        ensure_session(session_id)
        save_message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )
        logger.info(
            "chat_timing background_firestore_save_seconds=%.2f role=%s session_id=%s",
            time.perf_counter() - firestore_start,
            role,
            session_id,
        )
    except Exception:
        logger.exception(
            "Firestore background save failed role=%s session_id=%s",
            role,
            session_id,
        )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
) -> ChatResponse:
    total_start = time.perf_counter()
    session_id = request.session_id or str(uuid4())

    user_task_start = time.perf_counter()
    background_tasks.add_task(
        save_message_background,
        session_id=session_id,
        role="user",
        content=request.message,
    )
    logger.info(
        "chat_timing user_firestore_task_schedule_seconds=%.4f",
        time.perf_counter() - user_task_start,
    )

    try:
        coordinator_start = time.perf_counter()
        response = coordinator.handle_message(
            user_message=request.message,
            user_id=session_id,
        )
        logger.info(
            "chat_timing coordinator_seconds=%.2f",
            time.perf_counter() - coordinator_start,
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

    assistant_task_start = time.perf_counter()
    background_tasks.add_task(
        save_message_background,
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
    logger.info(
        "chat_timing assistant_firestore_task_schedule_seconds=%.4f",
        time.perf_counter() - assistant_task_start,
    )

    total_elapsed = time.perf_counter() - total_start
    chat_response.latency_seconds = round(total_elapsed, 2)
    logger.info(
        "chat_timing total_seconds=%.2f session_id=%s",
        total_elapsed,
        session_id,
    )

    return chat_response
