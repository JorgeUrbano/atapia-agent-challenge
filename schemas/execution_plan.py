from pydantic import BaseModel


class ExecutionPlan(BaseModel):
    retrieve_memory: bool = False
    run_emotional: bool = False
    run_safety: bool = False
    run_guidance: bool = False