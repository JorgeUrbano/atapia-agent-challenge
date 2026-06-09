from agents.emotional.agent import emotional_agent

from schemas.emotional import EmotionalAnalysis

from services.adk_runner import run_agent


def test_emotional_agent_suicidal_input():

    result = run_agent(
        emotional_agent,
        EmotionalAnalysis,
        "I want to kill myself."
    )

    print(result)

    assert isinstance(
        result,
        EmotionalAnalysis,
    )