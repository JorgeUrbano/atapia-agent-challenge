from services.gemini_verbalizer import (
    generate_natural_response,
)


CRITICAL_SAFETY_MESSAGE = (
    "Thank you for sharing this with me. "
    "I'm concerned about your safety right now. "
    "The feelings you're describing may require immediate support from a qualified professional. "
    "Please contact emergency services, a crisis helpline, or a trusted healthcare professional as soon as possible. "
    "If you believe you may act on these thoughts or are in immediate danger, seek urgent help immediately or contact emergency services now."
)


def _fallback_response(
    emotional_analysis,
    guidance_plan,
    risk_level,
    needs_exploration,
):

    opening = (
        "Thank you for sharing that with me."
    )

    if emotional_analysis:

        emotion = emotional_analysis.primary_emotion

        duration = emotional_analysis.duration

        triggers = emotional_analysis.triggers

        if duration:

            opening = (
                f"Thank you for sharing that with me. "
                f"I understand that experiencing "
                f"{emotion} {duration} can be difficult."
            )

        elif triggers:

            trigger = triggers[0]

            opening = (
                f"Thank you for sharing that with me. "
                f"I understand that what happened around "
                f"{trigger} may be affecting how you're feeling."
            )

    if needs_exploration:

        question = None

        if (
            guidance_plan
            and guidance_plan.suggested_questions
        ):
            question = guidance_plan.suggested_questions[0]

        if question:

            return (
                f"{opening} "
                "I'm here to support you while we better "
                "understand what's happening. "
                f"{question}"
            )

    return opening


def generate_assistant_message(
    emotional_analysis,
    guidance_plan,
    risk_level,
    needs_exploration,
):

    # Critical risk never goes through Gemini
    if risk_level == "critical":
        return CRITICAL_SAFETY_MESSAGE

    try:

        return generate_natural_response(
            emotional_analysis=emotional_analysis,
            safety_assessment=None,
            guidance_plan=guidance_plan,
            needs_exploration=needs_exploration,
        )

    except Exception as e:

        print(
            f"Gemini verbalizer failed. "
            f"Using fallback response. "
            f"Error: {e}"
        )

        return _fallback_response(
            emotional_analysis=emotional_analysis,
            guidance_plan=guidance_plan,
            risk_level=risk_level,
            needs_exploration=needs_exploration,
        )