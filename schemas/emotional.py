from pydantic import BaseModel, Field


class EmotionalAnalysis(BaseModel):
    primary_emotion: str = "unknown"
    intensity: float = 0.0


class EmotionalSupportResponse(BaseModel):
    reflection: str = Field(
        description="Brief reflection of the user's emotional state."
    )
    validation: str = Field(
        description="Supportive validation without overclaiming."
    )
    supportive_message: str = Field(
        description="Warm response to the user."
    )