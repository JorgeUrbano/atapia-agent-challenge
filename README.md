# Atapia

Atapia is a multi-agent emotional support assistant based on Cognitive Behavioral Therapy principles. It uses Google Cloud, Vertex AI, ADK-style agent orchestration, FastAPI, Firestore and a web chat interface to provide early emotional support, emotional analysis, safety detection, guidance planning and session memory.

## Live Demo

https://atapia-demo-64988831476.europe-west1.run.app

## What it does

- Emotional support chat.
- Emotional analysis.
- Safety risk detection.
- CBT-inspired guidance.
- Session memory.
- Firestore persistence.
- Safety-first fast path for critical cases.

## Architecture

```txt
User
-> Web Chat
-> FastAPI /chat
-> Coordinator
-> Safety Agent
-> Emotional Agent
-> Guidance Agent
-> Fast/Gemini Verbalizer
-> Firestore
-> Response
```

- Coordinator: orchestrates the flow and builds the final response.
- Safety Agent: detects risk and activates safety bypass for critical cases.
- Emotional Agent: extracts structured emotional signals.
- Guidance Agent: proposes CBT-inspired guidance and exploration questions.
- MemoryService: keeps lightweight session context.
- Firestore: stores sessions and messages.
- Frontend: demo chat UI with session_id and diagnostics.

## Google Cloud / Vertex AI usage

- Vertex AI / Gemini for agent reasoning.
- Google ADK-style agent architecture.
- Firestore for persistence.
- Cloud Run for deployment.
- Cloud Build / Artifact Registry for container build/deploy.

## Demo cases

1. `I feel lonely since my divorce.`

   Demonstrates emotional analysis and supportive exploration.

2. `I still feel bad.`

   Demonstrates session memory and context continuity.

3. `I feel stressed at work.`

   Demonstrates a different emotional context.

4. `I want to kill myself.`

   Demonstrates critical safety detection and safety-first bypass.

## Local development

```bash
source venv/bin/activate
ATAPIA_FAST_VERBALIZER=true uvicorn api.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/
```

## Environment variables

```bash
ATAPIA_FAST_VERBALIZER=true
ATAPIA_AGENT_JSON_RETRY=false
```

- `ATAPIA_FAST_VERBALIZER=true`: uses a faster local verbalization path for demo responsiveness while keeping the multi-agent analysis flow.
- `ATAPIA_AGENT_JSON_RETRY=false`: avoids duplicating LLM calls by default; robust parsing and coordinator fallbacks remain active.

## Disclaimer

Atapia is a hackathon demo for emotional support and early intervention. It is not a medical device, therapy service or emergency service. In crisis situations, users should contact emergency services or qualified professionals.
