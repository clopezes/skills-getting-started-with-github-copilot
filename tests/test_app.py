import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}" + "/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    response_first = client.post(
        f"/activities/{quote(activity_name, safe='')}" + "/signup",
        params={"email": email},
    )
    assert response_first.status_code == 200

    # Act
    response_second = client.post(
        f"/activities/{quote(activity_name, safe='')}" + "/signup",
        params={"email": email},
    )

    # Assert
    assert response_second.status_code == 400
    assert response_second.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "removeme@mergington.edu"

    signup_response = client.post(
        f"/activities/{quote(activity_name, safe='')}" + "/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}" + "/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}" + "/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
