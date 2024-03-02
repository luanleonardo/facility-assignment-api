import pytest

from src.models import AssignmentProblem, CostProblem
from src.services import compute_cost_matrix


@pytest.fixture
def cost_problem(assignment_request):
    subset_clients = assignment_request.clients[:10]
    return CostProblem(
        clients=subset_clients, facilities=assignment_request.facilities
    )


def test_assignment_problem_model(cost_problem):

    cost_matrix = compute_cost_matrix(cost_problem)

    assignment_problem = AssignmentProblem(
        clients=cost_problem.clients,
        facilities=cost_problem.facilities,
        cost_matrix=cost_matrix,
    )

    assert assignment_problem.cost_matrix.shape == (3, 10)
