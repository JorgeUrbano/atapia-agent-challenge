from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.emotional import EmotionalAnalysis

emotional_agent = Agent(
    model="gemini-2.5-flash",
    name="emotional",
    description="Analyzes the user's emotional state and extracts structured emotional information.",
    instruction=(
    "Analyze the user's emotional state. "

    "Identify: "
    "1. Primary emotion. "
    "2. Secondary emotions. "
    "3. Emotional intensity. "
    "4. Duration if explicitly mentioned. "
    "5. Triggers if explicitly mentioned. "
    "6. Behavioral signals if explicitly mentioned. "

    "The primary emotion must be one of the following values: "
    "sadness, anxiety, stress, loneliness, frustration, guilt, fear, anger, grief, unknown. "

    "Secondary emotions should use the same categories when applicable. "

    "Behavioral signals may include examples such as: "
    "substance_use, social_withdrawal, avoidance, sleep_problems, overeating. "

        
    "Use information explicitly present in: "

    "- Known context (if provided)"
    "- Current message"

    "Known context contains information previously shared by the user. "

    "You may use both sources when identifying: "

    "- emotions"
    "- triggers"
    "- duration"
    "- behavioral signals"

    "Do not invent information that is not present in either source. "

    "Do not infer facts beyond the provided context. "

    "If the emotional state is unclear, use 'unknown'. "

    "Do not provide emotional support. "
    "Do not provide advice. "
    "Do not generate conversational responses. "

    "Return only structured emotional analysis."
),

    output_schema=EmotionalAnalysis,
)

root_agent = emotional_agent
