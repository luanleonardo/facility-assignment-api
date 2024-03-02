from typing import List, Tuple

import numpy as np

from src.models import (
    AlgorithmType,
    AssignmentProblem,
    AssignmentRequest,
    AssignmentSolution,
    Client,
    CostProblem,
    scale_clients_demands,
)
from src.services import (
    compute_cost_matrix,
    solve_flow_assignment_formulation,
    solve_milp_assignment_formulation,
)

ASSIGNMENT_ALGORITHM_MAPPING = {
    AlgorithmType.MCF_FORMULATION: solve_flow_assignment_formulation,
    AlgorithmType.MILP_FORMULATION: solve_milp_assignment_formulation,
}


def solve_facility_assignment(
    assignment_request: AssignmentRequest,
) -> AssignmentSolution:
    """Solve the facility assignment problem"""

    cost_problem = CostProblem(
        clients=assignment_request.clients,
        facilities=assignment_request.facilities,
        cost_type=assignment_request.objective,
    )

    cost_matrix = compute_cost_matrix(cost_problem)

    valid_cost_matrix, scaled_valid_clients = _handle_nans(
        assignment_request, cost_matrix
    )

    assignment_problem = AssignmentProblem(
        clients=scaled_valid_clients,
        facilities=cost_problem.facilities,
        cost_matrix=valid_cost_matrix,
        algorithm=assignment_request.algorithm,
    )

    return ASSIGNMENT_ALGORITHM_MAPPING[assignment_problem.algorithm](
        assignment_problem
    )


def _handle_nans(
    assignment_request: AssignmentRequest,
    cost_matrix: np.ndarray,
) -> Tuple[np.ndarray, List[Client]]:
    """
    Some pairs of (facility, client) may face an issue when computing their
    distance and receive a NaN. In this case, there is not much we can do but
    to remove them from the analysis.

    This means that we should remove all such columns from the `cost_matrix`,
    plus delete these clients from the request. Notice the remaining ones
    should be rescaled to keep the original total demand.
    """

    _, invalid_client_indices = np.nonzero(np.isnan(cost_matrix))
    unique_invalid_client_indices = np.unique(invalid_client_indices)
    valid_cost_matrix = np.delete(
        cost_matrix, unique_invalid_client_indices, axis=1
    )
    valid_clients = [
        client
        for i, client in enumerate(assignment_request.clients)
        if i not in unique_invalid_client_indices
    ]
    scaled_valid_clients = scale_clients_demands(
        clients=valid_clients,
        new_total_demand=assignment_request.total_demand,
    )

    return valid_cost_matrix, scaled_valid_clients
