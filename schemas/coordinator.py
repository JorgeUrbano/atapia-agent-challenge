from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.emotional import EmotionalAnalysis
from schemas.guidance import GuidancePlan
from schemas.safety import SafetyAssessment


class CoordinatorResponse(BaseModel):

    assistant_message: str = Field(
        default="",
        description="Final response shown to the user."
    )

    used_gemini: bool = Field(
        default=False,
        description="Whether Gemini generated the final response."
    )

    safety_bypassed: bool = Field(
        default=False,
        description=(
            "Whether the response bypassed Gemini due to "
            "critical safety handling."
        )
    )

    needs_exploration: bool = Field(
        default=False,
        description="Whether additional exploration is needed."
    )

    emotion: Optional[str] = Field(
        default=None,
        description="Primary detected emotion."
    )

    risk_level: Optional[str] = Field(
        default=None,
        description="Detected safety risk level."
    )

    cbt_focus: Optional[str] = Field(
        default=None,
        description="Selected CBT focus."
    )

    intervention_strategy: Optional[str] = Field(
        default=None,
        description="Suggested CBT intervention strategy."
    )

    suggested_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions."
    )

    emotional_analysis: Optional[EmotionalAnalysis] = Field(
        default=None,
        description="Full emotional analysis."
    )

    safety_assessment: Optional[SafetyAssessment] = Field(
        default=None,
        description="Full safety assessment."
    )

    guidance_plan: Optional[GuidancePlan] = Field(
        default=None,
        description="Full CBT guidance plan."
    )