import asyncio
import json
import logging
import time

from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


load_dotenv()


APP_NAME = "emotional_support"
USER_ID = "local_user"
logger = logging.getLogger("uvicorn.error")


def _timing_prefix(agent) -> str | None:
    agent_name = getattr(agent, "name", "")

    if agent_name == "emotional":
        return "emotional_timing"

    if agent_name == "guidance":
        return "guidance_timing"

    return None


async def _run_agent_async(
    agent,
    output_schema,
    user_message: str,
):
    timing_prefix = _timing_prefix(agent)
    total_start = time.perf_counter()
    prompt_start = time.perf_counter()

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

    if timing_prefix:
        logger.info(
            "%s prompt_build_seconds=%.2f",
            timing_prefix,
            time.perf_counter() - prompt_start,
        )

    llm_start = time.perf_counter()
    events = list(
        runner.run(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        )
    )
    if timing_prefix:
        logger.info(
            "%s llm_call_seconds=%.2f",
            timing_prefix,
            time.perf_counter() - llm_start,
        )

    parse_start = time.perf_counter()
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
    if timing_prefix:
        logger.info(
            "%s parse_seconds=%.2f",
            timing_prefix,
            time.perf_counter() - parse_start,
        )

    validation_start = time.perf_counter()
    result = output_schema.model_validate(data)
    if timing_prefix:
        logger.info(
            "%s schema_validation_seconds=%.2f",
            timing_prefix,
            time.perf_counter() - validation_start,
        )
        logger.info(
            "%s total_seconds=%.2f",
            timing_prefix,
            time.perf_counter() - total_start,
        )

    return result


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
