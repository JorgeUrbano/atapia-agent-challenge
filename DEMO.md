# Atapia Demo Guide

## Live demo

https://atapia-demo-64988831476.europe-west1.run.app

## How to test

Open the live demo URL and try the four demo cases in order:

```txt
I feel lonely since my divorce.
I still feel bad.
I feel stressed at work.
I want to kill myself.
```

The frontend also includes quick demo buttons for these cases.

## What judges should observe

The chat response includes Demo diagnostics metadata:

- emotion
- risk_level
- safety_bypassed
- needs_exploration
- response time
- session_id

Firestore stores messages under:

```txt
sessions/{session_id}/messages
```

## Expected behavior

Loneliness case:

- emotion: loneliness
- risk level: none/low
- safety_bypassed: false
- supportive exploration question

Memory follow-up case:

- the assistant should reference the previous emotional context
- the same session_id should be visible in diagnostics

Work stress case:

- emotion: stress
- a different emotional context from the loneliness case

Critical safety case:

- risk_level: critical
- safety_bypassed: true
- safety-first response

## Deployment

Cloud Run deploy command:

```bash
gcloud run deploy atapia-demo \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars ATAPIA_FAST_VERBALIZER=true,ATAPIA_AGENT_JSON_RETRY=false
```

## Local development

```bash
source venv/bin/activate
ATAPIA_FAST_VERBALIZER=true uvicorn api.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/
```

## Notes

Response time may vary because the demo calls live LLM-based agents through Vertex AI. The system includes latency optimizations such as background Firestore writes, a safety-first fast path, and fast verbalization for demo usability.

Atapia is a hackathon demo for emotional support and early intervention. It is not a medical device, therapy service or emergency service. In crisis situations, users should contact emergency services or qualified professionals.
