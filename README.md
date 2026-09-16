# VitaTwin

VitaTwin is an explainable personal-wellness digital twin. It turns a health profile and short daily check-ins into transparent scores, trends, attention flags, and small next steps. A what-if lab shows how the rules respond to lifestyle changes, while the coach can use either deterministic guidance or an optional AI provider.

> VitaTwin is a portfolio MVP and general wellness tool. It is not a medical device, does not diagnose conditions, and is not intended for emergencies.

## MVP functionality

- Email/password accounts with bcrypt password hashing and expiring JWT access.
- Health baseline: age, height, weight, smoking, alcohol, goals, and optional known conditions.
- One idempotent daily check-in with mood, stress, sleep, movement, hydration, resting heart rate, and notes.
- Explainable vitality score with six visible dimensions: sleep, activity, recovery, mood, lifestyle, and body.
- Fourteen-day trend, check-in streak, ranked recommendations, and plainly worded attention flags.
- What-if simulator that compares the current score with changed sleep, activity, stress, smoking, or weight inputs.
- Context-aware wellness coach with a safe deterministic fallback when no AI key is configured.
- Responsive React interface and production Docker images.

## Architecture

- **Frontend:** React 18, Vite, Axios, Lucide icons, responsive CSS.
- **API:** FastAPI, Pydantic, bcrypt/JWT authentication.
- **Database:** MongoDB with unique email and per-user daily check-in indexes.
- **Optional AI:** OpenAI-compatible chat-completions endpoint. Core scoring never depends on an LLM.

## Run locally

Docker Desktop is the shortest path:

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8080`. API documentation is available at `http://localhost:8000/docs`.

The app works without an AI key. Add `OPENAI_API_KEY` to `.env` only if you want provider-generated coach responses.

## Development

```bash
# API
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt pytest
MONGODB_URI=mongodb://localhost:27017 DATABASE_NAME=vitatwin_dev \
  JWT_SECRET=local-development-secret-change-me \
  uvicorn main:app --app-dir backend --reload

# Frontend
cd frontend
npm ci
npm run dev
```

## API surface

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET|PUT /api/v1/profile`
- `GET|POST /api/v1/checkins`
- `GET /api/v1/twin/dashboard`
- `POST /api/v1/twin/simulate`
- `POST /api/v1/twin/coach`
- `GET /health` and `GET /ready`

## Verification

```bash
pytest -q backend/tests
cd frontend
npm run check
npm run build
```

API integration tests use a disposable MongoDB database. Never point the test suite at production.
