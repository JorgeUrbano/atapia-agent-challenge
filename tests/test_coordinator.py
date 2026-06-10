from agents.coordinator.coordinator import Coordinator


def test_coordinator_exploration():

    coordinator = Coordinator()

    response = coordinator.handle_message(
        "I feel terrible"
    )

    assert response.needs_exploration is True

    assert response.assistant_message != ""