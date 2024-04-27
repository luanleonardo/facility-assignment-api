from copy import deepcopy
from typing import List

from src.models import AssignedFacility
from src.services import compute_service_area


def evaluate_assigned_facilities(
    assigned_facilities: List[AssignedFacility],
) -> List[AssignedFacility]:
    """Evaluate assigned facilities"""

    assigned_facilities_copy = deepcopy(assigned_facilities)

    # Compute facilities expected demand and service area
    for i, assigned_facility_i in enumerate(assigned_facilities_copy):
        assigned_facilities_copy[i].expected_demand = round(
            sum(
                client.demand
                for client in assigned_facility_i.assigned_clients
            )
        )
        assigned_facilities_copy[i].service_area = compute_service_area(
            assigned_facility_i
        )

    # Remove intersection between facilities service areas
    for i, assigned_facility_i in enumerate(assigned_facilities_copy):
        exclusive_area_i = assigned_facility_i.facility.exclusive_service_area
        if exclusive_area_i.is_empty:
            continue

        for j, assigned_facility_j in enumerate(assigned_facilities_copy):
            service_area_j = assigned_facility_j.service_area
            if i == j or service_area_j.is_empty:
                continue

            intersection = exclusive_area_i.intersection(service_area_j)
            if not intersection.is_empty:
                new_service_area = service_area_j.difference(intersection)
                assigned_facilities_copy[j].service_area = new_service_area

    # Compute the expected optimal distance of the TSP route to meet the
    # demand of clients assigned to each facility.
    for i, assigned_facility in enumerate(assigned_facilities_copy):
        service_area = assigned_facility.service_area
        num_assigned_clients = len(assigned_facility.assigned_clients)
        assigned_facilities_copy[i].expected_optimal_tsp_route_distance = (
            round(
                (
                    0.75
                    * (num_assigned_clients * service_area.area * 12_321)
                    ** 0.5
                ),
                ndigits=2,
            )
        )

    return assigned_facilities_copy
