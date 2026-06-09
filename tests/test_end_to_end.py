from agents.coordinator.coordinator import Coordinator
from schemas.coordinator import CoordinatorResponse


def test_end_to_end_emotional_case():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I've been feeling lonely since my divorce."
    )

    print("\nEMOTIONAL CASE:")
    print(result)

    assert isinstance(
        result,
        CoordinatorResponse,
    )

    assert result.emotion is not None

    assert result.cbt_focus is not None

    assert result.emotional_analysis is not None

    assert result.guidance_plan is not None


def test_end_to_end_stress_case():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I feel stressed at work."
    )

    print("\nSTRESS CASE:")
    print(result)

    assert isinstance(
        result,
        CoordinatorResponse,
    )

    assert result.emotion is not None

    assert result.cbt_focus is not None

    assert result.emotional_analysis is not None

    assert result.guidance_plan is not None


def test_end_to_end_suicidal_case():

    coordinator = Coordinator()

    result = coordinator.handle_message(
        "I want to kill myself."
    )

    print("\nSUICIDAL CASE:")
    print(result)

    assert isinstance(
        result,
        CoordinatorResponse,
    )

    assert result.emotion is not None

    assert result.risk_level == "critical"

    assert result.cbt_focus is not None

    assert result.safety_assessment is not None