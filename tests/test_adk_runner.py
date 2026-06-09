from agents.emotional.agent import emotional_agent

from schemas.emotional import EmotionalAnalysis

from services.adk_runner import run_agent


def test_emotional_runner_returns_schema():

    result = run_agent(
        emotional_agent,
        EmotionalAnalysis,
        "I've been feeling lonely since my divorce."
    )

    assert isinstance(
        result,
        EmotionalAnalysis,
    )

    assert result.primary_emotion == "loneliness"