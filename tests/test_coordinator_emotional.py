from agents.coordinator.coordinator import Coordinator


def test_coordinator_runs_emotional_agent():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I've been feeling lonely since my divorce."
    )

    assert result.emotional_analysis is not None

    assert result.emotion == "loneliness"