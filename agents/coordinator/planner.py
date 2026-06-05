from schemas.execution_plan import ExecutionPlan


class Planner:

    def create_plan(self, user_message: str) -> ExecutionPlan:

        return ExecutionPlan(
            retrieve_memory=False,
            run_emotional=True,
            run_safety=True,
            run_guidance=True,
        )