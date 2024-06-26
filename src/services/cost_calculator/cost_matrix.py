import cost_matrix
import numpy as np

from src.models import CostProblem, CostType

OSRM_COST_TYPE_MAPPING = {
    CostType.OSRM_DISTANCE.value: "distances",
    CostType.OSRM_DURATION.value: "durations",
}


def compute_cost_matrix(cost_problem: CostProblem) -> np.ndarray:
    """Compute cost matrix with a given cost type"""

    sources = np.array(
        [(facility.lat, facility.lng) for facility in cost_problem.facilities]
    )
    destinations = np.array(
        [(client.lat, client.lng) for client in cost_problem.clients]
    )
    demands = np.array([client.demand for client in cost_problem.clients])

    if cost_problem.cost_type == CostType.SPHERICAL_DISTANCE:
        return demands * cost_matrix.spherical(
            sources=sources, destinations=destinations
        )

    return demands * cost_matrix.osrm(
        sources=sources,
        destinations=destinations,
        server_address=cost_problem.osrm_server_address,
        batch_size=cost_problem.osrm_batch_size,
        cost_type=OSRM_COST_TYPE_MAPPING[cost_problem.cost_type.value],
    )
