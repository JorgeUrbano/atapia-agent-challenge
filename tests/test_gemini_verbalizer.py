from schemas.emotional import EmotionalAnalysis
from schemas.guidance import GuidancePlan

from services.gemini_verbalizer import (
    generate_natural_response,
)


def test_gemini_verbalizer():

    emotional_analysis = EmotionalAnalysis(
        primary_emotion="loneliness",
        secondary_emotions=[],
        intensity=0.6,
        duration="since divorce",
        triggers=["divorce"],
        behavioral_signals=[],
    )

    guidance_plan = GuidancePlan(
        cbt_focus="social_connection",
        clinical_rationale="test",
        intervention_strategy=(
            "Increase opportunities for social connection."
        ),
        exploration_targets=[],
        suggested_questions=[
            "How has your social life changed since your divorce?"
        ],
    )

    response = generate_natural_response(
        emotional_analysis=emotional_analysis,
        safety_assessment=None,
        guidance_plan=guidance_plan,
        needs_exploration=True,
    )

    print("\nGEMINI RESPONSE:\n")
    print(response)

    assert isinstance(response, str)
    assert len(response) > 0