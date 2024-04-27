import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

URL = "v1/solve-assignment"


@pytest.mark.parametrize(
    "invalid_request_json",
    [
        {
            "totalDemand": 100,
            "algorithm": 1,
            "objective": 1,
        },
        {
            "totalDemand": 100,
            "facilities": [],
            "clients": [],
            "algorithm": 1,
            "objective": 1,
        },
        {
            "totalDemand": 100,
            "facilities": [{"id": "0", "name": "FC1", "lat": 1.0, "lng": 1.0}],
            "clients": [{"id": "0", "lat": 1.0, "lng": 1.0}],
            "algorithm": 1,
            "objective": "invalid",
        },
    ],
)
def test_solve_assignment_validation_error(invalid_request_json):

    response = client.post(url=URL, json=invalid_request_json)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_solve_assignment(assignment_request_data):

    response = client.post(url=URL, json=assignment_request_data)

    assert response.status_code == status.HTTP_200_OK


def test_solve_assignment_infeasible(assignment_request_data):

    request_data = {
        "totalDemand": 100,
        "facilities": [
            {
                "id": "FC1",
                "name": "FC1",
                "lat": 1.0,
                "lng": 1.0,
                "minDemand": 200,
            },
            {"id": "FC2", "name": "FC2", "lat": 2.0, "lng": 2.0},
        ],
        "clients": [{"id": "C1", "lat": 1.5, "lng": 1.5}],
    }

    response = client.post(url=URL, json=request_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "No optimal solution found" in response.text
