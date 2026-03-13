import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict after each test."""

    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activities_dict():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant_and_updates_activity():
    email = "tester@example.com"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")

    data = client.get("/activities").json()
    assert email in data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate@example.com"
    first = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert first.status_code == 200

    second = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert second.status_code == 400
    assert second.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity_returns_404():
    response = client.post("/activities/NoSuchActivity/signup?email=test@example.com")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
