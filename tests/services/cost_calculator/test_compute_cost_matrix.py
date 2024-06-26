from uuid import uuid4

import numpy as np
import pytest
from mock import patch

from src.models import Client, CostProblem, CostType, Facility
from src.services import compute_cost_matrix


@pytest.fixture
def clients():
    coordinates = [(0.1, 0.1), (1.1, 1.1), (2.1, 2.1), (3.1, 3.1), (100, 100)]

    return [
        Client(id=str(uuid4()), lat=lat, lng=lng) for lat, lng in coordinates
    ]


@pytest.fixture
def clients_with_large_demands(clients):
    for client in clients:
        client.demand = 10

    return clients


@pytest.fixture
def facilities():
    facilities_data = [
        {"id": "1", "name": "Facility 1", "lat": 1, "lng": 1},
        {"id": "2", "name": "Facility 2", "lat": 2, "lng": 2},
        {"id": "3", "name": "Facility 3", "lat": 3, "lng": 3},
    ]

    return [Facility(**facility) for facility in facilities_data]


@pytest.fixture
def cost_problem(clients, facilities):
    return CostProblem(
        clients=clients,
        facilities=facilities,
        cost_type=CostType.SPHERICAL_DISTANCE,
    )


@pytest.fixture
def cost_problem_with_large_demands(clients_with_large_demands, facilities):
    return CostProblem(
        clients=clients_with_large_demands,
        facilities=facilities,
        cost_type=CostType.SPHERICAL_DISTANCE,
    )


@pytest.fixture
def mocked_osrm_cost_matrix(cost_problem):
    num_sources = len(cost_problem.facilities)
    num_destinations = len(cost_problem.clients)

    # Create a random generator
    seed = 2024
    rng = np.random.default_rng(seed)

    # Generate random matrix using the generator
    random_matrix = rng.random((num_sources, num_destinations))

    with patch(
        "src.services.cost_calculator.cost_matrix.cost_matrix.osrm"
    ) as mocked_osrm_cost_matrix_call:
        mocked_osrm_cost_matrix_call.return_value = random_matrix
        yield mocked_osrm_cost_matrix_call


def test_spherical_distance_matrix_computation(cost_problem):

    cost_matrix = compute_cost_matrix(cost_problem)

    num_sources = len(cost_problem.facilities)
    num_destinations = len(cost_problem.clients)

    assert cost_matrix.shape == (num_sources, num_destinations)


def test_spherical_distance_matrix_with_large_demands(
    cost_problem_with_large_demands,
):
    cost_matrix = compute_cost_matrix(cost_problem_with_large_demands)

    num_sources = len(cost_problem_with_large_demands.facilities)
    num_destinations = len(cost_problem_with_large_demands.clients)

    assert cost_matrix.shape == (num_sources, num_destinations)


@pytest.mark.parametrize(
    "cost_type",
    [CostType.OSRM_DISTANCE, CostType.OSRM_DURATION],
)
def test_osrm_cost_computation(
    mocked_osrm_cost_matrix, cost_problem, cost_type
):
    """
    Ensure the OSRM cost function is called instead of the spherical function
    """
    cost_problem.cost_type = cost_type
    compute_cost_matrix(cost_problem)

    mocked_osrm_cost_matrix.assert_called_once()
