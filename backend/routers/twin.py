import json

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
import httpx

from core.config import settings
from core.database import get_database
from core.security import current_user_id
from schemas import CoachIn, SimulationIn
from services.twin_engine import build_dashboard, simulate

router = APIRouter()


def context_for(user_id: str) -> tuple[dict, list[dict]]:
    user = get_database().users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("health_profile"):
        raise HTTPException(status_code=409, detail="Complete your health profile first")
    checkins = list(get_database().checkins.find({"user_id": ObjectId(user_id)}).sort("recorded_on", -1).limit(30))
    return user["health_profile"], checkins


@router.get("/dashboard")
def dashboard(user_id: str = Depends(current_user_id)):
    profile, checkins = context_for(user_id)
    return build_dashboard(profile, checkins)


@router.post("/simulate")
def run_simulation(payload: SimulationIn, user_id: str = Depends(current_user_id)):
    profile, checkins = context_for(user_id)
    return simulate(profile, checkins, payload.model_dump())


@router.post("/coach")
async def coach(payload: CoachIn, user_id: str = Depends(current_user_id)):
    profile, checkins = context_for(user_id)
    dashboard_data = build_dashboard(profile, checkins)
    lowered = payload.question.lower()
    emergency_terms = ("chest pain", "can't breathe", "cannot breathe", "suicide", "overdose", "unconscious")
    if any(term in lowered for term in emergency_terms):
        return {
            "answer": "This may need urgent help. Contact your local emergency service now, and do not rely on VitaTwin for emergency guidance.",
            "source": "safety-rule",
            "disclaimer": "VitaTwin is a wellness tracker, not a medical service.",
        }
    if not settings.openai_api_key:
        focus = dashboard_data["recommendations"][0]
        return {
            "answer": f"Based on your recent check-ins, start with this small step: {focus} Track it for a week and review the trend rather than judging one day.",
            "source": "deterministic-coach",
            "disclaimer": "General wellness information only; consult a qualified professional for medical advice.",
        }
    prompt = {
        "question": payload.question,
        "wellness_snapshot": {key: dashboard_data[key] for key in ("score", "status", "bmi", "dimensions", "flags", "recommendations")},
        "rules": [
            "Give concise, supportive general wellness guidance.",
            "Do not diagnose, prescribe, or claim certainty.",
            "Explain which supplied data supports each suggestion.",
            "Recommend professional care when symptoms or persistent concerns are mentioned.",
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
            f"{settings.openai_api_base.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={"model": settings.openai_model, "messages": [{"role": "system", "content": "You are VitaTwin, a cautious wellness coach."}, {"role": "user", "content": json.dumps(prompt)}]},
            )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Empty coach response")
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="The AI coach is temporarily unavailable") from exc
    return {"answer": answer, "source": settings.openai_model, "disclaimer": "General wellness information only; consult a qualified professional for medical advice."}
