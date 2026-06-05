from pydantic import BaseModel, Field


class GuidancePlan(BaseModel):
    summary: str = Field(description="Short summary of the situation.")
    next_steps: list[str] = Field(description="Small, practical next steps.")
    follow_up_question: str | None = Field(
        default=None,
        description="Optional question that helps refine the guidance.",
    )
