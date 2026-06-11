from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.emotional import EmotionalAnalysis

emotional_agent = Agent(
    model="gemini-2.5-flash",
    name="emotional",
    description="Analyzes the user's emotional state and extracts structured emotional information.",
    instruction=(
        "Return strict JSON matching EmotionalAnalysis. "
        "Return only valid JSON. "
        "Use double quotes for all keys and string values. "
        "Do not use markdown. "
        "Do not include explanations outside JSON. "
        "Do not include trailing commas. "
        "Use only Known context and Current message; do not invent facts. "
        "Primary emotion must be one of: sadness, anxiety, stress, loneliness, "
        "frustration, guilt, fear, anger, grief, unknown. "
        "Secondary emotions use the same categories when applicable. "
        "Intensity is a number from 0 to 1. "
        "Include duration, triggers, and behavioral_signals only when explicit. "
        "Behavioral signals may include substance_use, social_withdrawal, "
        "avoidance, sleep_problems, overeating. "
        "If unclear, use primary_emotion='unknown'. "
        "Do not provide support, advice, or conversational text."
    ),
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=350,
        response_mime_type="application/json",
    ),
    output_schema=EmotionalAnalysis,
)

root_agent = emotional_agent
