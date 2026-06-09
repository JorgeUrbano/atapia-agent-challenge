from dotenv import load_dotenv
from google import genai
import os

load_dotenv()


def test_vertex_connection():

    print(
        "GOOGLE_GENAI_USE_VERTEXAI=",
        os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
    )

    print(
        "GOOGLE_CLOUD_PROJECT=",
        os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    print(
        "GOOGLE_CLOUD_LOCATION=",
        os.getenv("GOOGLE_CLOUD_LOCATION")
    )

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: connection_ok",
    )

    print(response.text)

    assert "connection_ok" in response.text