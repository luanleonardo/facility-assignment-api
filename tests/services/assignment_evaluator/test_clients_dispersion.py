import numpy as np
import pytest

from src.models import Client
from src.services import solve_clients_dispersion_problem


@pytest.fixture
def repeated_clients():
    """Clients at positions (0, 0) and (3, 3) are provided twice"""

    return [
        Client(id="1", lat=0, lng=0),
        Client(id="2", lat=0, lng=0),
        Client(id="3", lat=1, lng=1),
        Client(id="4", lat=2, lng=2),
        Client(id="5", lat=3, lng=3),
        Client(id="6", lat=3, lng=3),
    ]


@pytest.mark.parametrize(
    "subset_size, expected_locations_array",
    [
        (4, np.array([[0, 0], [1, 1], [2, 2], [3, 3]], dtype=float)),
        (
            7,
            np.array(
                [[0, 0], [0, 0], [1, 1], [2, 2], [3, 3], [3, 3]], dtype=float
            ),
        ),
    ],
)
def test_solve_clients_dispersion_problem(
    subset_size, expected_locations_array, repeated_clients
):
    """
    The solver is a heuristic, but for small data we can get a predictable
    result. In this case, the data set has 6 elements, with 2 repetitions.
    Therefore, a sparse subset of size 4 should remove these repeats. If
    the subset size is not smaller than the number of clients, it must
    return all clients.
    """
    # When
    dispersed_clients = solve_clients_dispersion_problem(
        clients=repeated_clients, subset_size=subset_size
    )

    # Then
    locations_array = np.array(
        [(client.lat, client.lng) for client in dispersed_clients]
    )
    locations_array.sort(axis=0)

    assert np.array_equal(locations_array, expected_locations_array)
