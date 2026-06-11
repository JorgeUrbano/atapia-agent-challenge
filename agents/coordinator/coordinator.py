import logging
import time

from agents.coordinator.planner import Planner
from agents.coordinator.response_generator import (
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
