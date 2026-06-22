import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: preserve original in-memory state and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activities():
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_existing_returns_400():
    # Arrange
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})
    # Assert
    assert resp.status_code == 400


def test_signup_nonexistent_activity_returns_404():
    # Act
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    # Assert
    assert resp.status_code == 404


def test_remove_participant_success():
    # Arrange
    activity = "Programming Class"
    email = activities[activity]["participants"][0]
    assert email in activities[activity]["participants"]
    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_returns_404():
    # Arrange
    activity = "Programming Class"
    email = "ghost@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert resp.status_code == 404
