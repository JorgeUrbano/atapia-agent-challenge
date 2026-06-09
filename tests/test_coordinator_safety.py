from agents.coordinator.coordinator import Coordinator


def test_coordinator_runs_safety_agent():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I want to kill myself."
    )

    assert "[Safety analysis available]" in result