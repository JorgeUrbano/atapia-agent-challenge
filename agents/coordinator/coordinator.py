import logging
import os
import time

from agents.coordinator.planner import Planner
from agents.coordinator.response_generator import (
    CRITICAL_SAFETY_MESSAGE,
    generate_assistant_message,
)

from agents.emotional.agent import emotional_agent
from agents.guidance.agent import guidance_agent
from agents.safety.agent import safety_agent

from schemas.coordinator import CoordinatorResponse
from schemas.emotional import EmotionalAnalysis
from schemas.guidance import GuidancePlan
from schemas.safety import SafetyAssessment

from services.adk_runner import run_agent
from services.memory import MemoryService


logger = logging.getLogger("uvicorn.error")
FAST_VERBALIZER = (
    os.getenv("ATAPIA_FAST_VERBALIZER", "false").lower()
    == "true"
)


def detect_critical_safety_risk(message: str) -> bool:
    text = (message or "").lower()
    critical_patterns = [
        "kill myself",
        "killing myself",
        "suicide",
        "suicidal",
        "end my life",
        "take my own life",
        "want to die",
        "don't want to live",
        "do not want to live",
        "hurt myself",
        "suicidarme",
        "quiero suicidarme",
        "me quiero suicidar",
        "quitarme la vida",
        "acabar con mi vida",
        "quiero morirme",
        "no quiero vivir",
        "hacerme daño",
    ]
    return any(pattern in text for pattern in critical_patterns)


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def infer_response_theme(
    user_message: str,
    emotion: str | None,
    memory_context: str | None,
) -> str:
    text = f"{user_message or ''} {memory_context or ''}".lower()
    normalized_emotion = (emotion or "").lower()

    if (
        normalized_emotion == "loneliness"
        or _contains_any(
            text,
            [
                "lonely",
                "alone",
                "divorce",
                "separated",
                "isolated",
                "soledad",
                "solo",
                "divorcio",
            ],
        )
    ):
        return "loneliness"

    if (
        normalized_emotion == "stress"
        or _contains_any(
            text,
            [
                "work",
                "job",
                "stressed",
                "stress",
                "pressure",
                "overwhelmed",
                "trabajo",
                "estrés",
                "estres",
                "presionado",
            ],
        )
    ):
        return "work_stress"

    if (
        normalized_emotion == "anxiety"
        or _contains_any(
            text,
            [
                "anxious",
                "anxiety",
                "worried",
                "worry",
                "can't stop thinking",
                "preocupado",
                "ansiedad",
                "no puedo parar de pensar",
            ],
        )
    ):
        return "anxiety"

    if (
        normalized_emotion == "sadness"
        or _contains_any(
            text,
            [
                "sad",
                "depressed",
                "down",
                "bad",
                "triste",
                "deprimido",
                "mal",
            ],
        )
    ):
        return "sadness"

    return "generic"


def _question_from_guidance(guidance_result) -> str | None:
    if guidance_result and guidance_result.suggested_questions:
        return guidance_result.suggested_questions[0]

    return None


def _question_for_theme(theme: str, guidance_result) -> str:
    guidance_question = _question_from_guidance(guidance_result)
    if guidance_question:
        return guidance_question

    focus = (
        guidance_result.cbt_focus
        if guidance_result
        else None
    )
    if focus == "cognitive_reframing":
        return "What thought keeps coming back most often?"

    if focus == "problem_solving":
        return "Which part feels most actionable today?"

    questions = {
        "loneliness": "What part of the day feels hardest for you right now?",
        "work_stress": "What part of work is creating the most pressure right now?",
        "anxiety": "What worry is taking up the most space today?",
        "sadness": "What part of this feels heaviest right now?",
        "generic": "What feels like the hardest part to handle today?",
    }
    return questions.get(theme, questions["generic"])


def build_fast_assistant_message(
    user_message: str,
    emotion: str | None,
    guidance_result,
    needs_exploration: bool,
    memory_context=None,
) -> str:

    text = (user_message or "").lower()
    context = (memory_context or "").lower()
    theme = infer_response_theme(
        user_message=user_message,
        emotion=emotion,
        memory_context=memory_context,
    )
    question = _question_for_theme(theme, guidance_result)

    if theme == "loneliness":
        if "divorce" in text or "divorce" in context:
            body = (
                "That sounds really painful, especially if the divorce changed "
                "your daily routines and the people you used to rely on. "
                "A useful first step could be to choose one lonely moment in the "
                "day and plan one small connection around it: sending a message, "
                "taking a walk somewhere familiar, or arranging a low-pressure "
                "conversation with someone you trust."
            )
        else:
            body = (
                "Loneliness can feel heavier when connection starts to seem out "
                "of reach. One small step is to make connection concrete: pick "
                "one person, one message, or one place where being around others "
                "feels low-pressure, and put it into today's plan."
            )
    elif theme == "work_stress":
        body = (
            "Work stress can become exhausting when your mind keeps carrying it "
            "after the day ends. One practical step is to separate what is urgent "
            "from what is only worrying: write down the top three things on your "
            "mind, mark what can actually be acted on today, and leave the rest "
            "for a specific review time tomorrow."
        )
    elif theme == "anxiety":
        body = (
            "When anxiety loops, the mind often treats every worry as equally "
            "urgent. Try writing three short lines: the worry, the evidence you "
            "have right now, and the next smallest useful step. That can help "
            "move the worry from a loop into something more manageable."
        )
    elif theme == "sadness":
        if "divorce" in context:
            body = (
                "It makes sense that feeling bad could still be tied to the "
                "divorce and the changes around it. A small, realistic step is "
                "to choose one stabilizing action for today, such as eating "
                "something simple, getting outside briefly, or sending one honest "
                "message to someone safe."
            )
        else:
            body = (
                "Feeling low can make even ordinary things take more effort. "
                "Rather than trying to fix everything at once, choose one small "
                "action that supports your body or your day: a shower, a short "
                "walk, a meal, or writing down what has been weighing on you."
            )
    else:
        body = (
            "This sounds like something worth taking seriously, and it may help "
            "to make it a little more concrete. Try naming the main feeling, the "
            "situation that seems to trigger it, and one small thing you can do "
            "in the next hour to reduce the pressure."
        )

    if needs_exploration and question:
        return f"{body}\n\n{question}"

    return body


class Coordinator:

    def __init__(self, memory_service=None):
        self.planner = Planner()
        self.memory_service = memory_service or MemoryService()

    def handle_message(
        self,
        user_message: str,
        user_id: str = "local_user",
    ):

        total_start = time.perf_counter()

        deterministic_guard_start = time.perf_counter()
        if detect_critical_safety_risk(user_message):
            logger.info(
                "coordinator_timing deterministic_safety_guard_seconds=%.4f",
                time.perf_counter() - deterministic_guard_start,
            )
            logger.info(
                "coordinator_timing deterministic_safety_bypass=%s",
                True,
            )
            logger.info(
                "coordinator_timing safety_agent_seconds=%.2f",
                0.0,
            )
            logger.info(
                "coordinator_timing emotional_agent_seconds=%.2f",
                0.0,
            )
            logger.info(
                "coordinator_timing guidance_agent_seconds=%.2f",
                0.0,
            )
            logger.info(
                "coordinator_timing fast_verbalizer_enabled=%s",
                FAST_VERBALIZER,
            )
            logger.info(
                "coordinator_timing verbalizer_seconds=%.2f",
                0.0,
            )
            logger.info(
                "coordinator_timing total_seconds=%.2f user_id=%s",
                time.perf_counter() - total_start,
                user_id,
            )
            return CoordinatorResponse(
                assistant_message=CRITICAL_SAFETY_MESSAGE,
                used_gemini=False,
                safety_bypassed=True,
                needs_exploration=True,
                emotion=None,
                risk_level="critical",
            )

        logger.info(
            "coordinator_timing deterministic_safety_guard_seconds=%.4f",
            time.perf_counter() - deterministic_guard_start,
        )
        logger.info(
            "coordinator_timing deterministic_safety_bypass=%s",
            False,
        )

        planner_start = time.perf_counter()
        plan = self.planner.create_plan(user_message)
        logger.info(
            "coordinator_timing planner_seconds=%.2f",
            time.perf_counter() - planner_start,
        )

        memory_start = time.perf_counter()
        memory_context = self._build_memory_context(user_id)
        logger.info(
            "coordinator_timing memory_seconds=%.2f",
            time.perf_counter() - memory_start,
        )

        agent_message = self._with_memory_context(
            memory_context=memory_context,
            user_message=user_message,
        )

        emotional_result = None
        safety_result = None
        guidance_result = None

        if plan.run_safety:

            try:

                safety_start = time.perf_counter()
                safety_result = (
                    self._run_safety_agent(
                        agent_message
                    )
                )
                logger.info(
                    "coordinator_timing safety_agent_seconds=%.2f",
                    time.perf_counter() - safety_start,
                )

                if self._is_safety_fast_path(safety_result):
                    logger.info(
                        "coordinator_timing safety_fast_path=%s",
                        True,
                    )
                    logger.info(
                        "coordinator_timing emotional_agent_seconds=%.2f",
                        0.0,
                    )
                    logger.info(
                        "coordinator_timing guidance_agent_seconds=%.2f",
                        0.0,
                    )

                    memory_save_start = time.perf_counter()
                    self._store_memory(
                        user_id=user_id,
                        user_message=user_message,
                        emotional_result=emotional_result,
                    )
                    logger.info(
                        "coordinator_timing memory_save_seconds=%.2f",
                        time.perf_counter() - memory_save_start,
                    )

                    verbalizer_start = time.perf_counter()
                    response = self._synthesize_response(
                        plan=plan,
                        user_message=user_message,
                        memory_context=memory_context,
                        emotional_result=emotional_result,
                        safety_result=safety_result,
                        guidance_result=guidance_result,
                    )
                    logger.info(
                        "coordinator_timing verbalizer_seconds=%.2f",
                        time.perf_counter() - verbalizer_start,
                    )

                    logger.info(
                        "coordinator_timing total_seconds=%.2f user_id=%s",
                        time.perf_counter() - total_start,
                        user_id,
                    )

                    return response

                logger.info(
                    "coordinator_timing safety_fast_path=%s",
                    False,
                )

            except Exception as e:

                logger.exception(
                    "Safety agent failed: %s",
                    e,
                )

                safety_result = None

        if plan.run_emotional:

            try:

                emotional_start = time.perf_counter()
                emotional_result = (
                    self._run_emotional_agent(
                        agent_message
                    )
                )
                logger.info(
                    "coordinator_timing emotional_agent_seconds=%.2f",
                    time.perf_counter() - emotional_start,
                )

            except Exception as e:

                logger.exception(
                    "Emotional agent failed: %s",
                    e,
                )

                emotional_result = None

        if plan.run_guidance:

            try:

                guidance_start = time.perf_counter()
                guidance_result = (
                    self._run_guidance_agent(
                        agent_message
                    )
                )
                logger.info(
                    "coordinator_timing guidance_agent_seconds=%.2f",
                    time.perf_counter() - guidance_start,
                )

            except Exception as e:

                logger.exception(
                    "Guidance agent failed: %s",
                    e,
                )

                guidance_result = None

        memory_save_start = time.perf_counter()
        self._store_memory(
            user_id=user_id,
            user_message=user_message,
            emotional_result=emotional_result,
        )
        logger.info(
            "coordinator_timing memory_save_seconds=%.2f",
            time.perf_counter() - memory_save_start,
        )

        verbalizer_start = time.perf_counter()
        response = self._synthesize_response(
            plan=plan,
            user_message=user_message,
            memory_context=memory_context,
            emotional_result=emotional_result,
            safety_result=safety_result,
            guidance_result=guidance_result,
        )
        logger.info(
            "coordinator_timing verbalizer_seconds=%.2f",
            time.perf_counter() - verbalizer_start,
        )

        logger.info(
            "coordinator_timing total_seconds=%.2f user_id=%s",
            time.perf_counter() - total_start,
            user_id,
        )

        return response

    def _is_safety_fast_path(
        self,
        safety_result,
    ) -> bool:

        return (
            getattr(safety_result, "risk_level", None)
            == "critical"
        )

    def _build_memory_context(
        self,
        user_id: str,
    ) -> str:

        records = list(
            self.memory_service.list_for_user(user_id)
        )[-5:]

        if not records:
            return ""

        items = "\n".join(
            f"* {record.content}"
            for record in records
        )

        return f"Known context:\n{items}"

    def _with_memory_context(
        self,
        memory_context: str,
        user_message: str,
    ) -> str:

        if not memory_context:
            return user_message

        return (
            f"{memory_context}\n\n"
            f"Current message:\n{user_message}"
        )

    def _store_memory(
        self,
        user_id: str,
        user_message: str,
        emotional_result=None,
    ) -> None:

        memory = self._extract_demo_memory(
            user_message=user_message,
            emotional_result=emotional_result,
        )

        if not memory:
            return

        existing_memories = {
            record.content
            for record in self.memory_service.list_for_user(user_id)
        }

        if memory in existing_memories:
            return

        self.memory_service.add(
            user_id=user_id,
            content=memory,
        )

    def _extract_demo_memory(
        self,
        user_message: str,
        emotional_result=None,
    ):

        text = user_message.lower()

        if "divorce" in text:
            return "User is going through a divorce."

        if not emotional_result:
            return None

        emotion = emotional_result.primary_emotion

        if not emotion or emotion == "unknown":
            return None

        return f"User has reported {emotion}."

    def _run_emotional_agent(
        self,
        user_message: str,
    ):
        return run_agent(
            emotional_agent,
            EmotionalAnalysis,
            user_message,
        )

    def _run_safety_agent(
        self,
        user_message: str,
    ):
        return run_agent(
            safety_agent,
            SafetyAssessment,
            user_message,
        )

    def _run_guidance_agent(
        self,
        user_message: str,
    ):
        return run_agent(
            guidance_agent,
            GuidancePlan,
            user_message,
        )

    def _synthesize_response(
        self,
        plan,
        user_message,
        memory_context,
        emotional_result,
        safety_result,
        guidance_result,
    ):

        emotion = (
            emotional_result.primary_emotion
            if emotional_result
            else None
        )

        risk_level = (
            safety_result.risk_level
            if safety_result
            else None
        )

        cbt_focus = (
            guidance_result.cbt_focus
            if guidance_result
            else None
        )

        intervention_strategy = (
            guidance_result.intervention_strategy
            if guidance_result
            else None
        )

        suggested_questions = (
            guidance_result.suggested_questions
            if guidance_result
            else []
        )

        logger.info(
            "coordinator_timing fast_verbalizer_enabled=%s",
            FAST_VERBALIZER,
        )

        if (
            FAST_VERBALIZER
            and risk_level != "critical"
        ):
            assistant_message = build_fast_assistant_message(
                user_message=user_message,
                emotion=emotion,
                guidance_result=guidance_result,
                needs_exploration=plan.needs_exploration,
                memory_context=memory_context,
            )
            used_gemini = False
            safety_bypassed = False

        else:
            (
                assistant_message,
                used_gemini,
                safety_bypassed,
            ) = generate_assistant_message(
                emotional_analysis=emotional_result,
                guidance_plan=guidance_result,
                risk_level=risk_level,
                needs_exploration=plan.needs_exploration,
            )

        return CoordinatorResponse(
            assistant_message=assistant_message,
            used_gemini=used_gemini,
            safety_bypassed=safety_bypassed,
            needs_exploration=plan.needs_exploration,
            emotion=emotion,
            risk_level=risk_level,
            cbt_focus=cbt_focus,
            intervention_strategy=intervention_strategy,
            suggested_questions=suggested_questions,
            emotional_analysis=emotional_result,
            safety_assessment=safety_result,
            guidance_plan=guidance_result,
        )
