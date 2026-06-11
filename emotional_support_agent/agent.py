from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from pydantic import PrivateAttr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.coordinator.coordinator import Coordinator


class EmotionalSupportAgent(BaseAgent):
    """ADK root agent that delegates each user turn to the Python Coordinator."""

    _coordinator: Coordinator = PrivateAttr(default_factory=Coordinator)

    async def _run_async_impl(self, ctx: InvocationContext):
        user_message = self._extract_user_message(ctx)
        user_id = getattr(ctx.session, "user_id", None) or "local_user"

        response = await asyncio.to_thread(
            self._coordinator.handle_message,
            user_message,
            user_id,
        )

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=response.assistant_message,
                    )
                ],
            ),
            custom_metadata={
                "coordinator_executed": True,
                "used_gemini": response.used_gemini,
                "safety_bypassed": response.safety_bypassed,
                "emotion": response.emotion,
                "risk_level": response.risk_level,
            },
        )

    def _extract_user_message(self, ctx: InvocationContext) -> str:
        if not ctx.user_content or not ctx.user_content.parts:
            return ""

        text_parts = [
            part.text
            for part in ctx.user_content.parts
            if getattr(part, "text", None)
        ]

        return "\n".join(text_parts)


root_agent = EmotionalSupportAgent(
    name="emotional_support_agent",
    description=(
        "Routes ADK user messages through the Atapia Coordinator pipeline."
    ),
)
