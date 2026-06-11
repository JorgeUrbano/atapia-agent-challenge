from __future__ import annotations

from typing import Any


def _client():
    from google.cloud import firestore

    return firestore.Client()


def ensure_session(session_id: str) -> None:
    from google.cloud import firestore

    session_ref = _client().collection("sessions").document(session_id)
    snapshot = session_ref.get()

    data = {
        "session_id": session_id,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    if not snapshot.exists:
        data["created_at"] = firestore.SERVER_TIMESTAMP

    session_ref.set(data, merge=True)


def save_message(
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    from google.cloud import firestore

    message_data: dict[str, Any] = {
        "role": role,
        "content": content,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    if metadata is not None:
        message_data["metadata"] = metadata

    (
        _client()
        .collection("sessions")
        .document(session_id)
        .collection("messages")
        .document()
        .set(message_data)
    )
