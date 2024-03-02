from copy import deepcopy
from typing import List

from pydantic import BaseModel, PositiveFloat


class Client(BaseModel):
    """Client model

    Attributes
    ----------
    id
        Unique identifier for the client.
    lat, lng
        Coordinates of the client
    demand
        Represents the client's demand, which can be a floating-point
        number, such as in a scenario with 100 clients and a total demand of
        150, where each demand would be 1.5.
    """

    id: str
    lat: float
    lng: float
    demand: PositiveFloat = 1.0


def scale_clients_demands(
    clients: List[Client], new_total_demand: float
) -> List[Client]:
    """Scale clients' demands to a new total demand"""

    clients_copy = deepcopy(clients)
    original_total_demand = sum(client.demand for client in clients)
    scale_factor = new_total_demand / original_total_demand

    for client in clients_copy:
        client.demand = round(scale_factor * client.demand, ndigits=2)

    return clients_copy
