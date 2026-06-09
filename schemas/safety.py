# schemas/safety.py

from typing import List, Literal

from pydantic import BaseModel, Field


RiskLevel = Literal[
    "none",
    "low",
    "medium",
    "high",
    "critical",
]

RiskIndicator = Literal[
    "hopelessness",
    "self_harm",
    "suicidal_ideation",
    "suicidal_plan",
    "substance_abuse",
]


class SafetyAssessment(BaseModel):
    risk_detected: bool = Field(
        description="Whether any safety concern was detected."
    )

    risk_level: RiskLevel = Field(
        description="Estimated safety risk level."
    )

    risk_indicators: List[RiskIndicator] = Field(
        default_factory=list,
        description="Safety indicators identified in the user's message."
    )

    requires_immediate_attention: bool = Field(
        description="Whether the situation requires immediate attention."
    )