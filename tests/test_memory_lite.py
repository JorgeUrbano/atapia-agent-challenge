import agents.coordinator.coordinator as coordinator_module

from agents.coordinator.coordinator import Coordinator
from schemas.emotional import EmotionalAnalysis
from schemas.guidance import GuidancePlan
from schemas.safety import SafetyAssessment
from services.memory import MemoryService


def _fake_run_agent(agent, output_schema, user_message):
    text = user_message.lower()

    if output_schema is EmotionalAnalysis:
        emotion = "loneliness" if "lonely" in text else "unknown"

        return EmotionalAnalysis(
            primary_emotion=emotion,
            secondary_emotions=[],
            intensity=0.5,
            duration=None,
            triggers=[],
            behavioral_signals=[],
        )

    if output_schema is SafetyAssessment:
        critical = "kill myself" in text

        return SafetyAssessment(
            risk_detected=critical,
            risk_level="critical" if critical else "none",
            risk_indicators=(
                ["suicidal_ideation"]
                if critical
                else []
            ),
            requires_immediate_attention=critical,
        )

    if output_schema is GuidancePlan:
        return GuidancePlan(
            cbt_focus="exploration",
            clinical_rationale="More context is needed.",
            intervention_strategy="Ask a focused follow-up question.",
            exploration_targets=[],
            suggested_questions=[
                "What feels hardest right now?"
            ],
        )

    raise AssertionError(
        f"Unexpected output schema: {output_schema}"
    )


def _fake_generate_assistant_message(
    emotional_analysis,
    guidance_plan,
    risk_level,
    needs_exploration,
):
    return (
        "demo response",
        risk_level != "critical",
        risk_level == "critical",
    )


def test_memory_lite_injects_prior_context(monkeypatch):
    captured_messages = []

    def capture_run_agent(agent, output_schema, user_message):
        captured_messages.append(user_message)
        return _fake_run_agent(
            agent,
            output_schema,
            user_message,
        )

    monkeypatch.setattr(
        coordinator_module,
        "run_agent",
        capture_run_agent,
    )
    monkeypatch.setattr(
        coordinator_module,
        "generate_assistant_message",
        _fake_generate_assistant_message,
    )

    memory = MemoryService()
    coordinator = Coordinator(memory_service=memory)

    coordinator.handle_message(
        "I am going through a divorce.",
        user_id="demo_user",
    )
    coordinator.handle_message(
        "I feel lonely.",
        user_id="demo_user",
    )
    result = coordinator.handle_message(
        "It's getting worse.",
        user_id="demo_user",
    )

    records = list(memory.list_for_user("demo_user"))
    memory_contents = [
        record.content
        for record in records
    ]

    assert "User is going through a divorce." in memory_contents
    assert "User has reported loneliness." in memory_contents

    first_turn_messages = captured_messages[:3]

    assert all(
        message == "I am going through a divorce."
        for message in first_turn_messages
    )

    third_turn_messages = captured_messages[-3:]

    assert all(
        "Known context:" in message
        for message in third_turn_messages
    )
    assert all(
        "User is going through a divorce." in message
        for message in third_turn_messages
    )
    assert all(
        "User has reported loneliness." in message
        for message in third_turn_messages
    )
    assert all(
        "Current message:\nIt's getting worse." in message
        for message in third_turn_messages
    )

    assert result.assistant_message == "demo response"
    assert result.emotional_analysis is not None
    assert result.guidance_plan is not None


def test_memory_lite_keeps_critical_safety_bypass(monkeypatch):
    monkeypatch.setattr(
        coordinator_module,
        "run_agent",
        _fake_run_agent,
    )
    monkeypatch.setattr(
        coordinator_module,
        "generate_assistant_message",
        _fake_generate_assistant_message,
    )

    memory = MemoryService()
    coordinator = Coordinator(memory_service=memory)

    coordinator.handle_message(
        "I am going through a divorce.",
        user_id="demo_user",
    )
    result = coordinator.handle_message(
        "I want to kill myself.",
        user_id="demo_user",
    )

    assert result.risk_level == "critical"
    assert result.safety_bypassed is True
    assert result.used_gemini is False
