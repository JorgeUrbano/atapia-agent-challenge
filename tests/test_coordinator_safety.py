from agents.coordinator.coordinator import Coordinator


def test_coordinator_runs_safety_agent():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I want to kill myself."
    )

    assert result.safety_assessment is not None

    assert result.risk_level == "critical"

    assert result.safety_bypassed is True

    assert result.used_gemini is False