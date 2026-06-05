from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    user_id: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryService:
    """Small in-memory store that can be swapped for ADK memory later."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def add(self, user_id: str, content: str) -> MemoryRecord:
        record = MemoryRecord(id=str(uuid4()), user_id=user_id, content=content)
        self._records.append(record)
        return record

    def list_for_user(self, user_id: str) -> Iterable[MemoryRecord]:
        return tuple(record for record in self._records if record.user_id == user_id)

    def clear(self) -> None:
        self._records.clear()
