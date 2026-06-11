import asyncio
import json
import logging
import os
import time

from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


load_dotenv()


APP_NAME = "emotional_support"
USER_ID = "local_user"
logger = logging.getLogger("uvicorn.error")
AGENT_JSON_RETRY = (
    os.getenv("ATAPIA_AGENT_JSON_RETRY", "false").lower()
    == "true"
)


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()

    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if not lines:
        return stripped

    if lines[0].strip().startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def _extract_json_object(text: str) -> str:
    start_index = text.find("{")
    if start_index == -1:
        return text.strip()

    depth = 0
    in_string = False
    is_escaped = False

    for index in range(start_index, len(text)):
        char = text[index]

        if in_string:
            if is_escaped:
                is_escaped = False
            elif char == "\\":
                is_escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start_index:index + 1].strip()

    return text[start_index:].strip()


def parse_json_output(final_text: str, log_failure: bool = True) -> dict:
    try:
        return json.loads(final_text)
    except json.JSONDecodeError:
        pass

    cleaned_text = _strip_markdown_fence(final_text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    extracted_text = _extract_json_object(cleaned_text)

    try:
        return json.loads(extracted_text)
    except json.JSONDecodeError:
        if log_failure:
            logger.error(
                "agent_json_parse_failed raw_output=%r",
                final_text[:1000],
            )
        raise


def _parse_json_candidates(
    text_outputs: list[str],
    log_failure: bool = True,
) -> dict:
    candidates = list(reversed(text_outputs))

    if len(text_outputs) > 1:
        candidates.extend(
            [
                "".join(text_outputs),
                "\n".join(text_outputs),
            ]
        )

    last_error = None
    for index, candidate in enumerate(candidates):
        try:
            return parse_json_output(
                candidate,
                log_failure=False,
            )
        except json.JSONDecodeError as error:
            last_error = error

    raw_output = "".join(text_outputs)
    if log_failure:
        logger.error(
            "agent_json_parse_failed raw_output=%r",
            raw_output[:1000],
        )
    if last_error:
        raise last_error

    raise RuntimeError("Agent did not return parseable JSON output.")


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
    log_parse_failure: bool = True,
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
    text_outputs = []
    final_text_outputs = []

    for event in events:
        is_final_response = (
            event.is_final_response()
            if hasattr(event, "is_final_response")
            else False
        )

        if not getattr(event, "content", None):
            continue

        if not event.content.parts:
            continue

        for part in event.content.parts:

            if hasattr(part, "text") and part.text:
                text_outputs.append(part.text)
                if is_final_response:
                    final_text_outputs.append(part.text)

    selected_text_outputs = final_text_outputs or text_outputs

    if not selected_text_outputs:
        raise RuntimeError(
            "Agent did not return any text output."
        )

    try:
        data = _parse_json_candidates(
            selected_text_outputs,
            log_failure=log_parse_failure and not final_text_outputs,
        )
    except json.JSONDecodeError:
        if not final_text_outputs:
            raise
        data = _parse_json_candidates(
            text_outputs,
            log_failure=log_parse_failure,
        )
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
    agent_name = getattr(agent, "name", "unknown")

    try:
        return asyncio.run(
            _run_agent_async(
                agent=agent,
                output_schema=output_schema,
                user_message=user_message,
                log_parse_failure=not AGENT_JSON_RETRY,
            )
        )
    except json.JSONDecodeError:
        if not AGENT_JSON_RETRY:
            logger.warning(
                "agent_json_parse_failed_no_retry agent=%s",
                agent_name,
            )
            raise

        logger.warning(
            "agent_json_retry_enabled agent=%s",
            agent_name,
        )
        retry_message = (
            f"{user_message}\n\n"
            "System retry: the previous structured output was invalid or "
            "truncated. Return one complete valid JSON object only, matching "
            "the requested schema exactly. Do not include markdown or text "
            "outside the JSON object."
        )
        return asyncio.run(
            _run_agent_async(
                agent=agent,
                output_schema=output_schema,
                user_message=retry_message,
                log_parse_failure=True,
            )
        )
