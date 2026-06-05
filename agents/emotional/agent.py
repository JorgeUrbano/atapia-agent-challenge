from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.emotional import EmotionalSupportResponse

emotional_agent = Agent(
    model="gemini-2.5-flash",
    name="emotional",
    description="Provides empathetic emotional support and reflection.",
    instruction=(
        "Offer emotionally attuned, non-judgmental support. "
        "Reflect the user's feelings, normalize difficult emotions without minimizing them, "
        "and avoid giving clinical diagnoses."
    ),
    output_schema=EmotionalSupportResponse,
)

root_agent = emotional_agent
