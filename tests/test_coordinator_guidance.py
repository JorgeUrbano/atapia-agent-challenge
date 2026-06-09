from agents.coordinator.coordinator import Coordinator


def test_coordinator_runs_guidance_agent():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I've been feeling lonely since my divorce."
    )

    assert "[Guidance available]" in result