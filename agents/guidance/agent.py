from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.guidance import GuidancePlan

guidance_agent = Agent(
    model="gemini-2.5-flash",
    name="guidance",
    description="Suggests practical next steps and coping strategies.",
    instruction=(
        "Give grounded, actionable guidance. Keep steps small, realistic, and respectful "
        "of the user's autonomy. Avoid medical, legal, or financial certainty."
    ),
    output_schema=GuidancePlan,
)

root_agent = guidance_agent
