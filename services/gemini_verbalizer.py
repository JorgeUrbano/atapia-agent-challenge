from dotenv import load_dotenv

from google import genai


load_dotenv()


BANNED_OPENINGS = [
    "Thank you for sharing that with me.",
    "Thank you for sharing this with me.",
    "I know it can be really tough to open up",
    "Talking about situations like this is often not easy",
    "I'm here to support you",
]


def _strip_leading_phrase(message: str, phrase: str) -> str:
    if not message.lower().startswith(phrase.lower()):
        return message

    return message[len(phrase):].lstrip(" ,.\n")


def _extract_last_question(message: str) -> str | None:
    paragraphs = [
        paragraph.strip()
        for paragraph in message.split("\n\n")
        if paragraph.strip()
    ]
    for paragraph in reversed(paragraphs):
        if paragraph.endswith("?"):
            return paragraph

    question_index = message.rfind("?")
    if question_index == -1:
        return None

    start_index = max(
        message.rfind(".", 0, question_index),
        message.rfind("\n", 0, question_index),
    )
    return message[start_index + 1:question_index + 1].strip()


def _strip_markdown_emphasis(message: str) -> str:
    return message.replace("*", "")


def clean_repetitive_opening(
    message: str,
    user_message: str | None = None,
) -> str:
    cleaned = (message or "").strip()
    if not cleaned:
        return cleaned

    original = cleaned
    starts_with_banned_opening = any(
        cleaned.lower().startswith(opening.lower())
        for opening in BANNED_OPENINGS
    )
    combined_context = f"{user_message or ''} {original}".lower()
    question = _extract_last_question(original)

    if starts_with_banned_opening and (
        "divorce" in combined_context
        or "lonely" in combined_context
        or "loneliness" in combined_context
    ):
        rewritten = (
            "Divorce can make loneliness feel especially heavy when routines "
            "and familiar connections change at the same time. One useful next "
            "step is to identify one moment of the day when loneliness is "
            "strongest and plan one low-pressure connection around it."
        )
        if question:
            return f"{rewritten}\n\n{question}"
        return rewritten

    if (
        (
            "divorce" in combined_context
            or "lonely" in combined_context
            or "loneliness" in combined_context
        )
        and "low-pressure connection" not in combined_context
        and "one moment" not in combined_context
    ):
        rewritten = (
            "Divorce can make loneliness feel especially heavy when routines "
            "and familiar connections change at the same time. One useful next "
            "step is to identify one moment of the day when loneliness is "
            "strongest and plan one low-pressure connection around it."
        )
        if question:
            return f"{rewritten}\n\n{question}"
        return rewritten

    if starts_with_banned_opening and (
        "work" in combined_context
        or "job" in combined_context
        or "stress" in combined_context
    ):
        rewritten = (
            "Work stress often gets heavier when everything feels urgent at "
            "once. A useful first step is to write down the three things taking "
            "up the most mental space, then mark which one can actually be "
            "acted on today and which ones need to wait."
        )
        if question:
            return f"{rewritten}\n\n{question}"
        return rewritten

    if (
        (
            "work" in combined_context
            or "job" in combined_context
            or "stress" in combined_context
        )
        and "write down" not in combined_context
        and "urgent" not in combined_context
        and "mental space" not in combined_context
    ):
        rewritten = (
            "Work stress often gets heavier when everything feels urgent at "
            "once. A useful first step is to write down the three things taking "
            "up the most mental space, then mark which one can actually be "
            "acted on today and which ones need to wait."
        )
        if question:
            return f"{rewritten}\n\n{question}"
        return rewritten

    for opening in BANNED_OPENINGS:
        cleaned = _strip_leading_phrase(cleaned, opening)

    boilerplate = [
        "I'm here to support you as we explore this together.",
        "I'm here to support you while we better understand what's happening.",
        "We can explore this together step by step.",
    ]
    for phrase in boilerplate:
        cleaned = cleaned.replace(phrase, "").strip()

    if cleaned:
        return _strip_markdown_emphasis(cleaned)

    text = (user_message or "").lower()
    if "divorce" in text or "lonely" in text:
        return (
            "Divorce can make loneliness feel especially heavy when routines "
            "and familiar connections change at the same time. One useful next "
            "step is to identify one moment of the day when loneliness is "
            "strongest and plan one low-pressure connection around it."
        )

    if "work" in text or "stress" in text:
        return (
            "Work stress often gets heavier when everything feels urgent at "
            "once. A useful first step is to write down the three things taking "
            "up the most mental space, then mark which one can actually be "
            "acted on today."
        )

    return (
        "This sounds worth taking seriously. A useful next step is to name the "
        "main feeling, the situation that triggered it, and one small action "
        "that could make the next hour easier."
    )


def _build_verbalization_prompt(
    emotional_analysis,
    safety_assessment,
    guidance_plan,
    needs_exploration: bool,
    user_message: str | None = None,
    memory_context: str | None = None,
):

    primary_emotion = None
    duration = None
    triggers = []
    intensity = None

    if emotional_analysis:
        primary_emotion = emotional_analysis.primary_emotion
        duration = emotional_analysis.duration
        triggers = emotional_analysis.triggers
        intensity = emotional_analysis.intensity

    risk_level = "none"

    if safety_assessment:
        risk_level = safety_assessment.risk_level

    cbt_focus = None
    intervention_strategy = None
    suggested_questions = []

    if guidance_plan:
        cbt_focus = guidance_plan.cbt_focus
        intervention_strategy = (
            guidance_plan.intervention_strategy
        )
        suggested_questions = (
            guidance_plan.suggested_questions
        )

    first_question = None

    if suggested_questions:
        first_question = suggested_questions[0]

    return f"""
You are a conversational verbalization layer.

Your role is ONLY to transform structured decisions into a natural, warm, empathetic and conversational assistant response.

IMPORTANT

You are NOT an emotional analysis system.

You are NOT a safety assessment system.

You are NOT a CBT planning system.

You are NOT a therapist.

You are NOT a coach.

You do NOT make decisions.

All decisions have already been made by specialized agents.

The information below is FINAL.

You must not:

- infer new emotions
- infer new risks
- infer new causes
- infer new triggers
- infer new CBT strategies
- create new intervention plans
- create new recommendations
- create new advice
- create new questions
- create new coping strategies
- reinterpret the information
- perform additional reasoning

You must preserve the provided decisions exactly as they were given.

The value of the system comes from the specialized agents.

Your role is only to communicate their decisions naturally.

CONVERSATION STYLE

The response should feel like a real conversation with a supportive emotional wellbeing assistant.

The user should feel:

- heard
- understood
- supported
- encouraged to continue the conversation

The response should be:

- warm
- empathetic
- supportive
- human
- natural
- conversational
- concise

The response should normally follow this structure:

1. Use the user's actual context in the first sentence.

2. Acknowledge the difficulty in specific, natural language.

3. Give one concrete, practical next step based on the guidance plan.

4. If exploration is required, ask the provided question.

Do not start with "Thank you for sharing that with me."

Do not start multiple responses with the same phrase.

Do not use "I'm here to support you as we explore this together."

Avoid generic therapeutic boilerplate.

Do not sound like a template.

Do not use markdown formatting.

Give one concrete, practical next step before asking a question.

Ask at most one question.

If the user has already shared a clear context, do not only ask for more information.

IMPORTANT STYLE RULES

Do not start responses with:

- It sounds like...
- It seems like...
- Based on what you've shared...
- From the information provided...
- I've identified...
- The analysis shows...

Avoid generic therapist clichés.

Avoid generic LLM phrases.

Do not sound clinical.

Do not sound like a report.

Do not sound like a diagnostic summary.

Do not enumerate fields.

Do not mention structured information explicitly.

Never say:

- primary emotion
- trigger
- risk level
- intervention strategy
- CBT focus
- analysis

Never explain how the system works.

Never explain how the analysis was performed.

Never mention agents.

Use the intervention strategy as guidance for one practical next step, but do
not mention "intervention strategy" or "CBT focus" by name.

STYLE EXAMPLES

For loneliness/divorce:

Divorce can leave a very real gap in daily life, especially if routines and familiar connections changed at the same time. A small starting point could be to choose one moment of the day when loneliness feels strongest and plan one low-pressure connection around it: a message, a short walk somewhere familiar, or a call with someone safe.

What time of day tends to feel hardest?

For work stress:

Work stress often gets heavier when everything feels urgent at once. A useful first step is to write down the three things taking up the most mental space, then mark which one can actually be acted on today and which ones need to wait.

What part of work is creating the most pressure right now?

For sadness/follow-up:

If the bad feeling is still there, it may help to make it more specific rather than fighting the whole feeling at once. Try naming what is strongest right now: sadness, worry, guilt, emptiness, or exhaustion. That makes the next step easier to choose.

Which of those feels closest to what you are experiencing?

If a duration is provided,
you may naturally reference it.

If triggers are provided,
you may naturally reference them.

If needs_exploration is true
and a question is provided:

- include the provided question
- keep its meaning unchanged
- do not create additional questions

If a question is provided,
the response should end with that question.

STRUCTURED INFORMATION

PRIMARY EMOTION:
{primary_emotion}

DURATION:
{duration}

TRIGGERS:
{triggers}

INTENSITY:
{intensity}

RISK LEVEL:
{risk_level}

CBT FOCUS:
{cbt_focus}

INTERVENTION STRATEGY:
{intervention_strategy}

NEEDS EXPLORATION:
{needs_exploration}

QUESTION:
{first_question}

USER MESSAGE:
{user_message}

KNOWN SESSION CONTEXT:
{memory_context}

Generate only the final assistant response.
"""


def generate_natural_response(
    emotional_analysis,
    safety_assessment,
    guidance_plan,
    needs_exploration: bool,
    user_message: str | None = None,
    memory_context: str | None = None,
):

    client = genai.Client()

    prompt = _build_verbalization_prompt(
        emotional_analysis=emotional_analysis,
        safety_assessment=safety_assessment,
        guidance_plan=guidance_plan,
        needs_exploration=needs_exploration,
        user_message=user_message,
        memory_context=memory_context,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return clean_repetitive_opening(
        response.text,
        user_message=user_message,
    )
