from schemas.emotional import EmotionalAnalysis
from schemas.guidance import GuidancePlan

from services.gemini_verbalizer import (
    clean_repetitive_opening,
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


def test_clean_repetitive_opening_removes_thank_you_start():

    response = clean_repetitive_opening(
        "Thank you for sharing that with me. "
        "Divorce can make loneliness feel especially heavy.\n\n"
        "What time of day tends to feel hardest?",
    )

    assert not response.startswith("Thank you for sharing")


def test_clean_repetitive_opening_removes_support_boilerplate():

    response = clean_repetitive_opening(
        "Work stress often gets heavier when everything feels urgent. "
        "I'm here to support you as we explore this together.\n\n"
        "What part of work is creating the most pressure right now?",
    )

    assert "I'm here to support you as we explore this together" not in response


def test_clean_repetitive_opening_strengthens_generic_work_stress():

    response = clean_repetitive_opening(
        "It's understandable to feel stressed at work. "
        "What specific aspects of your work are causing stress?",
        user_message="I feel stressed at work.",
    )

    assert response.startswith("Work stress often gets heavier")
    assert "write down the three things" in response
    assert response.count("?") <= 1
