from datetime import date

from services.twin_engine import calculate_snapshot, simulate


def test_scoring_is_bounded_and_explainable():
    profile = {"height_cm": 180, "weight_kg": 80, "smoker": False, "alcohol_per_week": 0, "sleep_goal_hours": 8}
    checkin = {"recorded_on": date.today(), "mood": 4, "stress": 4, "sleep_hours": 8, "active_minutes": 45, "steps": 9000}
    result = calculate_snapshot(profile, [checkin])
    assert 0 <= result["score"] <= 100
    assert result["bmi"] == 24.7
    assert len(result["recommendations"]) == 3


def test_healthier_scenario_improves_score():
    profile = {"height_cm": 180, "weight_kg": 95, "smoker": True, "alcohol_per_week": 10, "sleep_goal_hours": 8}
    checkin = {"recorded_on": date.today(), "mood": 2, "stress": 9, "sleep_hours": 5, "active_minutes": 5, "steps": 1500}
    result = simulate(profile, [checkin], {"sleep_hours": 8, "active_minutes": 45, "stress": 4, "smoker": False})
    assert result["delta"] > 0
