from typing import Literal

from pydantic import BaseModel, Field


class SafetyAssessment(BaseModel):
    risk_level: Literal["low", "moderate", "high", "imminent"] = Field(
        description="Estimated safety risk level."
    )
    concern: str = Field(description="Main safety concern, if any.")
    recommended_action: str = Field(description="Immediate safety recommendation.")
