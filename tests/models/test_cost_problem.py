import pytest
from pydantic import ValidationError

from config import settings
from src.models import CostProblem, CostType, ObjectiveType


@pytest.mark.parametrize(
    "cost_type",
    [
        CostType.SPHERICAL_DISTANCE,
        CostType.OSRM_DISTANCE,
        CostType.OSRM_DURATION,
    ],
)
def test_cost_problem_model(clients, facilities, cost_type):

    cost_problem = CostProblem(
        clients=clients, facilities=facilities, cost_type=cost_type
    )

    assert cost_problem.clients == clients
    assert cost_problem.facilities == facilities
    assert cost_problem.cost_type == cost_type
    assert cost_problem.osrm_batch_size == settings.OSRM_BATCH_SIZE
    assert cost_problem.osrm_server_address == settings.OSRM_SERVER_ADDRESS


@pytest.mark.parametrize(
    "cost_type, expected_cost_type",
    [
        (
            ObjectiveType.MIN_PROXIMITY,
            CostType.SPHERICAL_DISTANCE,
        ),
        (
            ObjectiveType.MIN_TRAVEL_DISTANCE,
            CostType.OSRM_DISTANCE,
        ),
        (
            ObjectiveType.MIN_TRAVEL_DURATION,
            CostType.OSRM_DURATION,
        ),
    ],
)
def test_cost_problem_type_validation(
    clients, facilities, cost_type, expected_cost_type
):

    cost_problem = CostProblem(
        clients=clients, facilities=facilities, cost_type=cost_type
    )

    assert cost_problem.cost_type == expected_cost_type


def test_cost_problem_type_error(clients, facilities):
    with pytest.raises(ValidationError):
        CostProblem(
            clients=clients,
            facilities=facilities,
            cost_type=-1,
        )


def test_cost_problem_from_assignment_request(assignment_request):

    cost_problem = CostProblem(
        clients=assignment_request.clients,
        facilities=assignment_request.facilities,
        cost_type=assignment_request.objective,
    )

    assert cost_problem.clients == assignment_request.clients
    assert cost_problem.facilities == assignment_request.facilities
    assert cost_problem.cost_type == CostType.SPHERICAL_DISTANCE
