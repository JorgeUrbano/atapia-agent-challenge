# tests/test_memory_demo.py
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from agents.coordinator.coordinator import Coordinator

coordinator = Coordinator()

messages = [
    "I am going through a divorce.",
    "I feel lonely.",
    "It's getting worse.",
]

for message in messages:

    print("\n" + "=" * 80)
    print("USER:")
    print(message)

    response = coordinator.handle_message(
        message,
        user_id="demo_user",
    )

    print("\nASSISTANT:")
    print(response.assistant_message)

    print("\nEMOTION:")
    print(response.emotion)

    print("\nRISK:")
    print(response.risk_level)