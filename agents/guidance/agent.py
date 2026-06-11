from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.guidance import GuidancePlan


GUIDANCE_AGENT_INSTRUCTIONS = """
Return strict JSON matching GuidancePlan.
Analyze the situation from a CBT perspective only.
Do not identify emotions, assess safety, provide support, or write the final user response.
Use only Known context and Current message; do not invent facts.

Choose one cbt_focus from:
behavioral_activation, cognitive_reframing, problem_solving, emotion_regulation,
stress_management, social_connection, grief_processing, self_compassion, exploration.

Keep output concise:
- clinical_rationale: one short analytical sentence.
- intervention_strategy: one brief CBT-oriented strategy.
- exploration_targets: at most 2 short items.
- suggested_questions: at most 1 focused question.

If information is insufficient, use cbt_focus="exploration" and one question
that gathers the most useful next detail.
"""


guidance_agent = Agent(
    model="gemini-2.5-flash",
    name="guidance",
    description=(
        "Analyzes situations from a CBT perspective and recommends "
        "structured intervention strategies."
    ),
    instruction=GUIDANCE_AGENT_INSTRUCTIONS,
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=360,
    ),
    output_schema=GuidancePlan,
)

root_agent = guidance_agent
