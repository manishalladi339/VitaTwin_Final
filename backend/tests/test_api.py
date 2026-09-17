from datetime import date


PROFILE = {
    "age": 31,
    "height_cm": 168,
    "weight_kg": 72,
    "smoker": False,
    "alcohol_per_week": 2,
    "activity_goal_minutes": 150,
    "sleep_goal_hours": 8,
    "conditions": [],
}


def test_account_profile_checkin_dashboard_simulation_and_coach(client, account):
    headers = account["headers"]
    assert client.get("/api/v1/auth/me", headers=headers).json()["profile_complete"] is False
    profile = client.put("/api/v1/profile", headers=headers, json=PROFILE)
    assert profile.status_code == 200
    assert profile.json()["height_cm"] == 168

    checkin = client.post(
        "/api/v1/checkins",
        headers=headers,
        json={"recorded_on": str(date.today()), "mood": 4, "stress": 6, "sleep_hours": 6.5, "active_minutes": 25, "steps": 6400, "water_liters": 2.2, "resting_heart_rate": 68, "note": "Busy day"},
    )
    assert checkin.status_code == 200
    assert checkin.json()["note"] == "Busy day"

    # A second check-in for the same date updates the daily record instead of duplicating it.
    assert client.post("/api/v1/checkins", headers=headers, json={**checkin.json(), "mood": 5}).status_code == 200
    assert len(client.get("/api/v1/checkins", headers=headers).json()) == 1

    dashboard = client.get("/api/v1/twin/dashboard", headers=headers)
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert 0 <= data["score"] <= 100
    assert set(data["dimensions"]) == {"sleep", "activity", "recovery", "mood", "lifestyle", "body"}
    assert data["checkin_count"] == 1

    scenario = client.post("/api/v1/twin/simulate", headers=headers, json={"sleep_hours": 8, "active_minutes": 60, "stress": 3})
    assert scenario.status_code == 200
    assert scenario.json()["after"]["score"] >= scenario.json()["before"]["score"]

    coach = client.post("/api/v1/twin/coach", headers=headers, json={"question": "What should I focus on this week?"})
    assert coach.status_code == 200
    assert coach.json()["source"] == "deterministic-coach"


def test_authentication_and_validation_boundaries(client, account):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.post("/api/v1/auth/register", json={"name": "Again", "email": "maya@example.com", "password": "strongpass123"}).status_code == 409
    assert client.post("/api/v1/auth/login", json={"email": "maya@example.com", "password": "wrong-password"}).status_code == 401
    assert client.put("/api/v1/profile", headers=account["headers"], json={**PROFILE, "age": 5}).status_code == 422


def test_emergency_language_uses_safety_rule(client, account):
    client.put("/api/v1/profile", headers=account["headers"], json=PROFILE)
    response = client.post("/api/v1/twin/coach", headers=account["headers"], json={"question": "I have chest pain and cannot breathe"})
    assert response.status_code == 200
    assert response.json()["source"] == "safety-rule"
    assert "emergency" in response.json()["answer"].lower()


def test_password_byte_limit(client):
    response = client.post('/api/v1/auth/register', json={
        'name': 'Long Password', 'email': 'long@example.com', 'password': '🙂' * 20,
    })
    assert response.status_code == 422


def test_accounts_cannot_read_each_others_checkins(client, account):
    client.post('/api/v1/checkins', headers=account['headers'], json={
        'mood': 3, 'stress': 5, 'sleep_hours': 8, 'active_minutes': 30,
    })
    other = client.post('/api/v1/auth/register', json={
        'name': 'Other User', 'email': 'other@example.com', 'password': 'strongpass456',
    }).json()
    response = client.get('/api/v1/checkins', headers={'Authorization': f"Bearer {other['access_token']}"})
    assert response.status_code == 200
    assert response.json() == []
