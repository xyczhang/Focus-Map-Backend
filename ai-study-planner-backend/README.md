# AI Study Planner Backend

A Flask API that validates study preferences and uses the OpenAI Responses API to produce a structured study schedule.

## Endpoints

### `GET /health`

Returns `{ "status": "ok" }` when the service is available.

### `POST /generate-plan`

Accepts JSON containing 1–8 subjects and time preferences:

```json
{
  "subjects": [
    {"name": "Calculus", "deadline": "2026-10-15", "confidence": 2}
  ],
  "plan_days": 3,
  "available_minutes": 120,
  "session_minutes": 30,
  "break_minutes": 5
}
```

`plan_days` can be 1–7, and `available_minutes` is the time available on each day. The endpoint returns a summary, a day number for every study/break session, and a study tip. Invalid requests return a JSON error with status 400. Upstream generation failures return a safe JSON error with status 502.

## How the frontend communicates

The frontend sends a `POST` request to `/generate-plan` after the user submits the form. It renders each object in the returned `sessions` array as a schedule card. CORS is limited to the origins in `ALLOWED_ORIGINS`.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add a real OpenAI API key to `.env`, then run:

```bash
python app.py
```

Test the health endpoint at `http://127.0.0.1:5000/health`.

## Environment variables and security

- `OPENAI_API_KEY`: required secret used only by the backend.
- `OPENAI_MODEL`: optional; defaults to `gpt-4o-mini`.
- `ALLOWED_ORIGINS`: comma-separated list of frontend origins permitted by CORS.

`.env` is ignored by Git. Never put the OpenAI key in frontend code or commit it to GitHub. On Render, add the key under the service's Environment settings.

## Deploy to Render

1. Push this directory to its own public GitHub repository.
2. In Render, create a Blueprint or Web Service from that repository.
3. Set `OPENAI_API_KEY` to the secret API key.
4. Set `ALLOWED_ORIGINS` to the final GitHub Pages origin, such as `https://YOUR_USERNAME.github.io`.
5. Deploy and check `https://YOUR-SERVICE.onrender.com/health`.
