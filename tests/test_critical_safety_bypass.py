from agents.coordinator.response_generator import (
    generate_assistant_message,
)
from agents.coordinator.coordinator import (
    Coordinator,
    detect_critical_safety_risk,
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


def test_deterministic_safety_guard_detects_critical_phrase():

    assert detect_critical_safety_risk("I want to kill myself.")

    assert detect_critical_safety_risk("No quiero vivir.")


def test_deterministic_safety_guard_skips_agents():

    coordinator = Coordinator()

    def fail_agent_call(*args, **kwargs):
        raise AssertionError("No LLM agent should run for deterministic safety.")

    coordinator._run_safety_agent = fail_agent_call
    coordinator._run_emotional_agent = fail_agent_call
    coordinator._run_guidance_agent = fail_agent_call

    response = coordinator.handle_message(
        "I want to kill myself.",
        user_id="test-critical-fast-path",
    )

    assert response.risk_level == "critical"

    assert response.safety_bypassed is True

    assert response.emotion is None

    assert response.needs_exploration is True
