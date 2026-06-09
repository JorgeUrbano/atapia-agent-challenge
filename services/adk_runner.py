import asyncio
import json

from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


load_dotenv()


APP_NAME = "emotional_support"
USER_ID = "local_user"


async def _run_agent_async(
    agent,
    output_schema,
    user_message: str,
):
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=user_message
            )
        ],
    )

    events = list(
        runner.run(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        )
    )

    final_text = None

    for event in events:

        if not getattr(event, "content", None):
            continue

        if not event.content.parts:
            continue

        for part in event.content.parts:

            if hasattr(part, "text") and part.text:
                final_text = part.text

    if final_text is None:
        raise RuntimeError(
            "Agent did not return any text output."
        )

    data = json.loads(final_text)

    return output_schema.model_validate(data)


def run_agent(
    agent,
    output_schema,
    user_message: str,
):
    return asyncio.run(
        _run_agent_async(
            agent=agent,
            output_schema=output_schema,
            user_message=user_message,
        )
    )