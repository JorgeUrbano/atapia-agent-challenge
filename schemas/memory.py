from pydantic import BaseModel


class MemoryContext(BaseModel):
    summary: str = ""
    recurring_topics: list[str] = []