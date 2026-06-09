from schemas.coordinator import CoordinatorResponse


def test_coordinator_response_empty():

    response = CoordinatorResponse()

    assert response.needs_exploration is False

    assert response.emotion is None

    assert response.risk_level is None

    assert response.cbt_focus is None

    assert response.emotional_analysis is None

    assert response.safety_assessment is None

    assert response.guidance_plan is None

    assert response.assistant_message == ""

    assert response.intervention_strategy is None

    assert response.suggested_questions == []