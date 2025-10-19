# VitaTwin — Deployment Guide

## Backend (Render)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Env:
  - `MONGODB_URI`
  - `OPENAI_API_KEY`
  - `JWT_SECRET`
  - `CORS_ORIGINS` (comma-separated)

## Frontend (Vercel)
- Root: `frontend/`
- Env: `VITE_BACKEND_URL = https://your-render-backend.onrender.com`

## Local (Docker)
```bash
docker-compose up --build
```

## API Routes
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET  /api/auth/me`
- `GET  /api/user/profile` (JWT)
- `POST /api/mood/analyze` (JWT, GPT-4 turbo)
- `POST /api/summary` (JWT, GPT-4 turbo)
- `GET  /health`

## Pages
- `/` Dashboard/Onboarding
- `/mood` Mood Check
- `/summary` Text Summarizer
- `/profile` Profile (JWT)
- `404` Not found
