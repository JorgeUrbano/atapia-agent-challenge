from typing import List, Literal

from pydantic import BaseModel, Field


CBTFocus = Literal[
    "behavioral_activation",
    "cognitive_reframing",
    "problem_solving",
    "emotion_regulation",
    "stress_management",
    "social_connection",
    "grief_processing",
    "self_compassion",
    "exploration",
]


class GuidancePlan(BaseModel):

    cbt_focus: CBTFocus = Field(
        description="Primary CBT focus."
    )

    clinical_rationale: str = Field(
        description=(
            "Brief clinical explanation for why this focus was selected."
        )
    )

    intervention_strategy: str = Field(
        description="Suggested CBT strategy."
    )

    exploration_targets: List[str] = Field(
        default_factory=list,
        description="Topics worth exploring further."
    )

    suggested_questions: List[str] = Field(
        default_factory=list,
        description="Questions that may help advance the intervention."
    )