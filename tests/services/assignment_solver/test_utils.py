from config import settings
from src.models import AlgorithmType
from src.services import scale_assignment_problem_parameters


def test_scale_assignment_problem_parameters(assignment_problem):
    """Test scaling of assignment problem parameters"""

    factor_mapping = {
        AlgorithmType.MILP_FORMULATION: settings.MILP_SCALE_FACTOR,
        AlgorithmType.MCF_FORMULATION: settings.MCF_SCALE_FACTOR,
    }

    # Scale problem parameters to become integer
    scaled_clients, scaled_facilities, scaled_cost_matrix = (
        scale_assignment_problem_parameters(
            assignment_problem=assignment_problem,
            scale_factor=factor_mapping[assignment_problem.algorithm],
        )
    )

    assert all(isinstance(client.demand, int) for client in scaled_clients)
    assert all(
        isinstance(facility.min_demand, int)
        and isinstance(facility.max_demand, int)
        for facility in scaled_facilities
    )
    assert scaled_cost_matrix.dtype == int
