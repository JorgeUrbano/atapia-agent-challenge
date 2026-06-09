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


class Coordinator:

    def __init__(self):
        self.planner = Planner()

    def handle_message(self, user_message: str):

        plan = self.planner.create_plan(user_message)

        emotional_result = None
        safety_result = None
        guidance_result = None

        if plan.run_emotional:
            emotional_result = self._run_emotional_agent(
                user_message
            )

        if plan.run_safety:
            safety_result = self._run_safety_agent(
                user_message
            )

        if plan.run_guidance:
            guidance_result = self._run_guidance_agent(
                user_message
            )

        return self._synthesize_response(
            plan=plan,
            emotional_result=emotional_result,
            safety_result=safety_result,
            guidance_result=guidance_result,
        )

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

        assistant_message = generate_assistant_message(
            emotional_analysis=emotional_result,
            guidance_plan=guidance_result,
            risk_level=risk_level,
            needs_exploration=plan.needs_exploration,
        )

        return CoordinatorResponse(
            assistant_message=assistant_message,
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