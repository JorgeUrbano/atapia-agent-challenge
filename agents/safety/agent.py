from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.safety import SafetyAssessment

safety_agent = Agent(
    model="gemini-2.5-flash",
    name="safety",
    description="Assesses crisis or self-harm risk and recommends safety steps.",
    instruction=(
        "Assess the user's message for urgent safety concerns, including self-harm, "
        "harm to others, abuse, or immediate danger. If risk is high, recommend contacting "
        "local emergency services or a crisis line and encourage reaching a trusted person now."
    ),
    output_schema=SafetyAssessment,
)

root_agent = safety_agent
