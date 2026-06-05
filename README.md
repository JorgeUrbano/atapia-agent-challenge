# Atapia Agent Challenge

ADK-based emotional support assistant organized into specialized agents.

## Structure

- `agents/coordinator/agent.py`: ADK entrypoint that exposes `root_agent`.
- `agents/emotional/agent.py`: empathetic support agent.
- `agents/safety/agent.py`: safety and crisis-risk assessment agent.
- `agents/guidance/agent.py`: practical guidance agent.
- `services/memory/memory_service.py`: local memory service abstraction.
- `schemas/`: Pydantic contracts for agent outputs.

## Run With ADK

```bash
source venv/bin/activate
adk run agents/coordinator
```

For the ADK web UI:

```bash
source venv/bin/activate
adk web agents
```

You can also run specialized agents directly, for example:

```bash
adk run agents/safety
```
