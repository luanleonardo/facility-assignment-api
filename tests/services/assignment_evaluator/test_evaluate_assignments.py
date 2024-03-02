from math import isclose

from src.models import AssignedFacility
from src.services import evaluate_assigned_facilities


def test_evaluate_assigned_facilities(
    facility_within_square_center,
    other_facility_within_square_center,
    clients_within_square,
):
    """Test evaluate_assigned_facilities function"""

    assigned_facilities = [
        AssignedFacility(
            facility=facility_within_square_center,
            assigned_clients=clients_within_square,
        ),
        AssignedFacility(
            facility=other_facility_within_square_center,
            assigned_clients=[],
        ),
    ]

    evaluated_facilities = evaluate_assigned_facilities(assigned_facilities)

    assert all(
        isclose(
            evaluated_facility.expected_demand,
            sum(
                client.demand for client in evaluated_facility.assigned_clients
            ),
        )
        for evaluated_facility in evaluated_facilities
    )
    assert evaluated_facilities[0].service_area.is_empty
    assert isclose(evaluated_facilities[1].service_area.area, 1.0 - 0.125)
