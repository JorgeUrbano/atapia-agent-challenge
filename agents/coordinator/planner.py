from schemas.execution_plan import ExecutionPlan


class Planner:

    HIGH_RISK_KEYWORDS = [
        "kill myself",
        "suicide",
        "end my life",
        "hurt myself",
    ]

    MODERATE_RISK_KEYWORDS = [
        "disappear",
        "no reason to live",
        "no point",
        "hopeless",
    ]

    EMOTIONAL_KEYWORDS = [
        "sad",
        "lonely",
        "anxious",
        "anxiety",
        "stress",
        "stressed",
        "angry",
        "fear",
        "guilty",
        "grief",
    ]

    GUIDANCE_KEYWORDS = [
        "what can i do",
        "how can i",
        "help me",
        "advice",
    ]

    GREETINGS = [
        "hello",
        "hi",
        "good morning",
        "thanks",
        "thank you",
    ]

    def create_plan(self, user_message: str) -> ExecutionPlan:

        text = user_message.lower()

        if any(k in text for k in self.HIGH_RISK_KEYWORDS):
            return ExecutionPlan(
                run_emotional=True,
                run_safety=True,
                run_guidance=True,
                needs_exploration=True,
            )

        if any(k in text for k in self.MODERATE_RISK_KEYWORDS):
            return ExecutionPlan(
                run_emotional=True,
                run_safety=True,
                run_guidance=True,
                needs_exploration=True,
            )

        if any(k in text for k in self.EMOTIONAL_KEYWORDS):
            return ExecutionPlan(
                run_emotional=True,
                run_guidance=True,
                needs_exploration=True,
            )

        if any(k in text for k in self.GUIDANCE_KEYWORDS):
            return ExecutionPlan(
                run_guidance=True,
            )

        if any(k in text for k in self.GREETINGS):
            return ExecutionPlan()

        return ExecutionPlan(
            run_emotional=True,
            run_guidance=True,
            needs_exploration=True,
        )