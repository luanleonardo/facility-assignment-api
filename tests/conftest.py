import json

import humps
import pytest

from src.models import (
    AlgorithmType,
    AssignmentProblem,
    AssignmentRequest,
    Client,
    CostProblem,
    Facility,
)
from src.services import compute_cost_matrix

ASSIGNMENT_REQUEST_FILE = "tests/models/data/request.json"
CLIENTS_FILE = "tests/models/data/clients.json"
FACILITIES_FILE = "tests/models/data/facilities.json"


@pytest.fixture
def assignment_request_data():
    with open(ASSIGNMENT_REQUEST_FILE) as file:
        return json.load(file)


@pytest.fixture
def assignment_request(assignment_request_data):
    request_data = humps.decamelize(assignment_request_data)
    return AssignmentRequest(**request_data)


@pytest.fixture
def clients_data():
    with open(CLIENTS_FILE) as file:
        return humps.decamelize(json.load(file))


@pytest.fixture
def clients(clients_data):
    return [Client(**data) for data in clients_data]


@pytest.fixture
def facilities_data():
    with open(FACILITIES_FILE) as file:
        return humps.decamelize(json.load(file))


@pytest.fixture
def facilities(facilities_data):
    return [Facility(**data) for data in facilities_data]


@pytest.fixture
def coordinates_within_square():
    return [
        (0.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0),
        (1.0, 0.0),
        (0.5, 0.75),
        (0.25, 0.5),
        (0.5, 0.25),
        (0.75, 0.5),
    ]


@pytest.fixture
def clients_within_square(coordinates_within_square):
    """Clients with ids from 1 to 4 form a square of area 1.0.
    Clients with ids from 5 to 8 form a smaller square with an
    area of 0.125"""

    return [
        Client(id=str(i), lat=lat, lng=lng)
        for i, (lng, lat) in enumerate(coordinates_within_square, start=1)
    ]


@pytest.fixture
def facility_within_square_center():
    """Defines facility with id 0 and location at 0.5, 0.5.
    The exclusive service area is a square of area 1.0 and
    vertices at points:
    (0.5, 0.75), (0.25, 0.5), (0.5, 0.25), (0.75, 0.5)"""

    return Facility(
        id="0",
        name="Facility",
        lat=0.5,
        lng=0.5,
        exclusive_service_area={
            "type": "Polygon",
            "coordinates": [
                [
                    [0.5, 0.75],
                    [0.25, 0.5],
                    [0.5, 0.25],
                    [0.75, 0.5],
                    [0.5, 0.75],
                ]
            ],
        },
    )


@pytest.fixture
def other_facility_within_square_center():
    """Defines facility with id 1 and location at 0.5, 0.5.
    The exclusive service area is a square of area 1.0 and
    vertices at points:
    (0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0),"""

    return Facility(
        id="1",
        name="Other Facility",
        lat=0.5,
        lng=0.5,
        exclusive_service_area={
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, 0.0],
                    [0.0, 1.0],
                    [1.0, 1.0],
                    [1.0, 0.0],
                    [0.0, 0.0],
                ]
            ],
        },
    )


@pytest.fixture(
    params=[AlgorithmType.MILP_FORMULATION, AlgorithmType.MCF_FORMULATION]
)
def assignment_problem(request, facilities, clients):
    cost_problem = CostProblem(clients=clients[:10], facilities=facilities)
    cost_matrix = compute_cost_matrix(cost_problem)

    return AssignmentProblem(
        clients=clients[:10],
        facilities=facilities,
        cost_matrix=cost_matrix,
        algorithm=request.param,
    )
