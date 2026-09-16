from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any


def clamp(value: float, low: float = 0, high: float = 100) -> int:
    return round(max(low, min(high, value)))


def bmi(profile: dict[str, Any]) -> float:
    height_m = float(profile["height_cm"]) / 100
    return round(float(profile["weight_kg"]) / (height_m * height_m), 1)


def calculate_snapshot(profile: dict[str, Any], checkins: list[dict[str, Any]]) -> dict[str, Any]:
    latest = checkins[0] if checkins else {}
    sleep_goal = float(profile.get("sleep_goal_hours", 8))
    sleep = float(latest.get("sleep_hours", sleep_goal))
    active = int(latest.get("active_minutes", 30))
    stress = int(latest.get("stress", 5))
    mood = int(latest.get("mood", 3))
    steps = int(latest.get("steps", 5000))

    sleep_score = clamp(100 - abs(sleep - sleep_goal) * 18)
    activity_score = clamp((active / 30) * 65 + min(steps / 10000, 1) * 35)
    recovery_score = clamp(110 - stress * 10)
    mood_score = clamp(mood * 20)
    lifestyle_score = 100
    if profile.get("smoker"):
        lifestyle_score -= 35
    lifestyle_score -= min(int(profile.get("alcohol_per_week", 0)) * 2, 25)
    lifestyle_score = clamp(lifestyle_score)

    value_bmi = bmi(profile)
    body_score = clamp(100 - abs(value_bmi - 22.5) * 5)
    dimensions = {
        "sleep": sleep_score,
        "activity": activity_score,
        "recovery": recovery_score,
        "mood": mood_score,
        "lifestyle": lifestyle_score,
        "body": body_score,
    }
    overall = clamp(mean(dimensions.values()))
    flags: list[dict[str, str]] = []
    if value_bmi < 18.5 or value_bmi >= 30:
        flags.append({"level": "attention", "title": "BMI outside the usual reference range", "detail": "Use this as a conversation starter with a qualified clinician, not a diagnosis."})
    if sleep < 6:
        flags.append({"level": "attention", "title": "Short sleep", "detail": "Your latest check-in records fewer than six hours of sleep."})
    if stress >= 8:
        flags.append({"level": "attention", "title": "High reported stress", "detail": "Consider recovery time and seek support if this persists."})
    if profile.get("smoker"):
        flags.append({"level": "priority", "title": "Smoking is the strongest modifiable flag", "detail": "A clinician can help you choose an evidence-based quitting plan."})

    recommendations = sorted(
        [
            (sleep_score, "Protect a consistent sleep window close to your personal goal."),
            (activity_score, "Build toward 30 active minutes and 8,000–10,000 steps on most days."),
            (recovery_score, "Schedule a short recovery block: walking, breathing, or an offline break."),
            (mood_score, "Record what influenced your mood so patterns become easier to spot."),
            (lifestyle_score, "Focus on one sustainable lifestyle change rather than several at once."),
        ],
        key=lambda item: item[0],
    )
    return {
        "score": overall,
        "status": "building baseline" if len(checkins) < 3 else ("steady" if overall >= 70 else "needs attention"),
        "bmi": value_bmi,
        "dimensions": dimensions,
        "flags": flags,
        "recommendations": [text for _, text in recommendations[:3]],
        "latest_checkin": serialize_checkin(latest) if latest else None,
    }


def build_dashboard(profile: dict[str, Any], checkins: list[dict[str, Any]]) -> dict[str, Any]:
    snapshot = calculate_snapshot(profile, checkins)
    chronological = list(reversed(checkins[:14]))
    trend = [
        {
            "date": str(item["recorded_on"]),
            "sleep": item["sleep_hours"],
            "stress": item["stress"],
            "mood": item["mood"],
            "activity": item["active_minutes"],
        }
        for item in chronological
    ]
    dates = {str(item["recorded_on"]) for item in checkins}
    streak = 0
    day = date.today()
    while day.isoformat() in dates:
        streak += 1
        day -= timedelta(days=1)
    return {**snapshot, "trend": trend, "checkin_count": len(checkins), "streak": streak}


def simulate(profile: dict[str, Any], checkins: list[dict[str, Any]], changes: dict[str, Any]) -> dict[str, Any]:
    before = calculate_snapshot(profile, checkins)
    simulated_profile = dict(profile)
    simulated_latest = dict(checkins[0] if checkins else {"recorded_on": date.today(), "mood": 3, "stress": 5, "sleep_hours": 8, "active_minutes": 30, "steps": 5000})
    for key, value in changes.items():
        if value is None:
            continue
        if key in {"smoker", "weight_kg"}:
            simulated_profile[key] = value
        else:
            simulated_latest[key] = value
    after = calculate_snapshot(simulated_profile, [simulated_latest])
    return {
        "before": before,
        "after": after,
        "delta": after["score"] - before["score"],
        "explanation": "This is a transparent scenario estimate based on VitaTwin's wellness scoring rules. It is not a medical prediction.",
    }


def serialize_checkin(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("_id", "")),
        "recorded_on": str(item["recorded_on"]),
        "mood": item["mood"],
        "stress": item["stress"],
        "sleep_hours": item["sleep_hours"],
        "active_minutes": item["active_minutes"],
        "steps": item.get("steps", 0),
        "water_liters": item.get("water_liters", 0),
        "resting_heart_rate": item.get("resting_heart_rate"),
        "note": item.get("note", ""),
        "created_at": item.get("created_at"),
    }
