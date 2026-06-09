from typing import List, Optional

from pydantic import BaseModel, Field


class EmotionalAnalysis(BaseModel):

    primary_emotion: str = Field(
        description="Main detected emotion."
    )

    secondary_emotions: List[str] = Field(
        default_factory=list,
        description="Additional detected emotions."
    )

    intensity: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated emotional intensity from 0 to 1."
    )

    duration: Optional[str] = Field(
        default=None,
        description="How long the emotion has been present, only if explicitly mentioned."
    )

    triggers: List[str] = Field(
        default_factory=list,
        description="Emotion triggers explicitly mentioned by the user."
    )

    behavioral_signals: List[str] = Field(
        default_factory=list,
        description=(
            "Relevant behaviors explicitly mentioned by the user, "
            "such as substance_use, social_withdrawal, avoidance, "
            "sleep_problems, overeating, etc."
        )
    )