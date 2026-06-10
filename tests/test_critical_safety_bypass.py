from agents.coordinator.response_generator import (
    generate_assistant_message,
)


def test_critical_safety_bypass():

    (
        assistant_message,
        used_gemini,
        safety_bypassed,
    ) = generate_assistant_message(
        emotional_analysis=None,
        guidance_plan=None,
        risk_level="critical",
        needs_exploration=True,
    )

    assert used_gemini is False

    assert safety_bypassed is True

    assert "safety" in assistant_message.lower()