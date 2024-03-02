from copy import deepcopy
from typing import List, Tuple

import numpy as np

from src.models import AlgorithmType, AssignmentProblem, Client, Facility


def scale_assignment_problem_parameters(
    assignment_problem: AssignmentProblem, scale_factor: int
) -> Tuple[List[Client], List[Facility], np.ndarray]:
    """Scale problem factors to become integer"""

    scaled_clients = deepcopy(assignment_problem.clients)
    for client in scaled_clients:
        client.demand = round(scale_factor * client.demand)

    scaled_facilities = deepcopy(assignment_problem.facilities)
    for facility in scaled_facilities:
        facility.min_demand = round(scale_factor * facility.min_demand)
        facility.max_demand = round(scale_factor * facility.max_demand)

    scaled_cost_matrix = assignment_problem.cost_matrix.copy()
    scaled_cost_matrix *= scale_factor

    # If the problem is formulated as a flow problem, the cost matrix is
    # scaled to become unit cost.
    if assignment_problem.algorithm == AlgorithmType.MCF_FORMULATION:
        num_facilities = len(assignment_problem.facilities)
        num_clients = len(assignment_problem.clients)
        for i in range(num_facilities):
            for j in range(num_clients):
                scaled_cost_matrix[i][j] = (
                    scaled_cost_matrix[i][j]
                    / assignment_problem.clients[j].demand
                )

    return scaled_clients, scaled_facilities, scaled_cost_matrix.astype(int)
