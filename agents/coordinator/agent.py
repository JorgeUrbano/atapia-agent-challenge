from pathlib import Path
import sys

from google.adk.agents.llm_agent import Agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


root_agent = Agent(
    model="gemini-2.5-flash",
    name="coordinator",
    description="ADK entrypoint for the emotional support system.",
    instruction=(
        "You are the Coordinator Agent of an emotional support system. "
        "Do not delegate work to ADK subagents. "
        "Planning, agent execution, routing, and response synthesis are handled "
        "externally by the Python Coordinator implementation. "
        "Do not use agent transfers. "
        "Do not perform multi-agent delegation."
    ),
)