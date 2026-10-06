import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities_data(monkeypatch):
    activity_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["alex@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activity_data)
    return activity_data


@pytest.fixture
def client(activities_data):
    return TestClient(app_module.app)


def test_root_redirects_to_static_app(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data_without_caching(client):
    # Arrange
    expected_activity = {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 3,
        "participants": ["alex@mergington.edu"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}
    assert response.headers["cache-control"] == "no-store"


def test_signup_adds_participant(client, activities_data):
    # Arrange
    email = "sam@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "sam@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, activities_data):
    # Arrange
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities_data["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Participant not found for this activity"
    }


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "sam@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}