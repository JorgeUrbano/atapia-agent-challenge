from pathlib import Path
import sys
import asyncio
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

from agents.emotional.agent import emotional_agent
 

APP_NAME = "emotional_test"
USER_ID = "test_user"


async def main():

    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    print("SESSION CREATED")
    print(session)

    runner = Runner(
        app_name=APP_NAME,
        agent=emotional_agent,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="I've been feeling lonely for months since my divorce."
            )
        ],
    )

    print("\nRUNNER CREATED")
    print(runner)

    events = runner.run(
        user_id=USER_ID,
        session_id=session.id,
        new_message=message,
    )

    print("\nEVENTS:\n")

    for event in events:
        print(event)

load_dotenv()

asyncio.run(main())

print("VERTEX:", os.getenv("GOOGLE_GENAI_USE_VERTEXAI"))
print("PROJECT:", os.getenv("GOOGLE_CLOUD_PROJECT"))
print("LOCATION:", os.getenv("GOOGLE_CLOUD_LOCATION"))