# Atapia Demo

Atapia runs as a single FastAPI web app:

- Frontend: `/`
- API: `/chat`
- Healthcheck: `/health`
- API docs: `/docs`

## Run locally

Start the unified app:

```bash
ATAPIA_FAST_VERBALIZER=true uvicorn api.main:app --reload
```

If `uvicorn` is only installed in the local virtualenv:

```bash
ATAPIA_FAST_VERBALIZER=true venv/bin/python -m uvicorn api.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000
```

## Run with Docker

Build:

```bash
docker build -t atapia-demo .
```

Run:

```bash
docker run --rm -p 8080:8080 -e ATAPIA_FAST_VERBALIZER=true atapia-demo
```

Open:

```txt
http://127.0.0.1:8080
```

## Deploy to Cloud Run

Deploy from source:

```bash
gcloud run deploy atapia-demo \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars ATAPIA_FAST_VERBALIZER=true
```

If the target Google Cloud project requires explicit Vertex AI or Firestore
configuration, add the relevant values as environment variables. Example
placeholders:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west1
VERTEX_AI_LOCATION=europe-west1
```

Use the names expected by your local Google ADK / Vertex AI configuration.

## Demo cases

Run these cases in order from the frontend demo buttons:

```txt
I feel lonely since my divorce.
I still feel bad.
I feel stressed at work.
I want to kill myself.
```

## What each case demonstrates

- Case 1: emotional analysis.
- Case 2: memory/context with same session_id.
- Case 3: different emotional context.
- Case 4: safety-first fast path and safety bypass.

## Firestore check

Review persisted messages at:

```txt
sessions/{session_id}/messages
```

## Environment variables

Use:

```bash
ATAPIA_FAST_VERBALIZER=true
```

`FAST_GUIDANCE` can be treated as experimental if present; it is not the main demo mode.
