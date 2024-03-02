"""
The objective of the discrete p-dispersion problem is to choose p
among n given points, such that the minimum distance between any
pair of chosen points is the largest possible. The p-dispersion problem
is known to be NP-hard.
Possible areas of application include localization theory and
multi-criteria optimization. In this API, the application is to find a
dispersed subset of clients assigned to a facility to best represent
the facility's service area. This module brings together heuristics to
solve the p-dispersion problem.
"""

from typing import List

import numpy as np

from src.models import Client
from src.services import spherical_cost_matrix


def solve_clients_dispersion_problem(
    clients: List[Client], subset_size: int
) -> List[Client]:
    """
    Compute well dispersed subset of Clients.
    This uses the greedy construction heuristic explained
    in [1] to find a well dispersed subset of clients.
    Parameters
    ----------
    clients
        A list containing the clients for which the dispersion problem
        will be solved.
    subset_size
        The desired size of the subset.
    Returns
    -------
    List
        A subset of clients that maximizes the minimum distance between
        any pair of selected clients.
    References
    ----------
    [1] Erkut, E. (1994) "A comparison of p-dispersion heuristics."
        European Journal of Operational Research, 77(3), 422-428.
        doi:10.1016/0305-0548(94)90041-8
    """

    # If the subset size is not less than the number
    # of clients, return all clients
    if subset_size >= len(clients):
        return clients

    # Compute distance matrix
    client_locations = np.array(
        [(client.lat, client.lng) for client in clients]
    )
    distance_matrix = spherical_cost_matrix(client_locations, client_locations)

    # Begin adding the farthest pair
    selected_indices = list(
        np.unravel_index(distance_matrix.argmax(), distance_matrix.shape)
    )

    # Add elements until the subset size is reached
    while len(selected_indices) < subset_size:
        sub_distance_matrix = distance_matrix[selected_indices]

        # Add element with the greatest minimum distance among all pairs
        new_index = sub_distance_matrix.min(axis=0).argmax()
        selected_indices.append(new_index)

    return [clients[index] for index in selected_indices]
