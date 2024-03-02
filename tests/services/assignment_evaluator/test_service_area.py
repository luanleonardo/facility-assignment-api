from math import isclose

from src.models import AssignedFacility
from src.services import compute_service_area


def test_compute_service_area(
    facility_within_square_center, clients_within_square
):
    """Test compute_service_area function"""

    # The assigned clients at the vertices of the exclusive
    # area and outside it, those outside form a square of
    # area 1.0
    assigned_facility = AssignedFacility(
        facility=facility_within_square_center,
        assigned_clients=clients_within_square,
    )

    # The service area should be a multipolygon that contains
    # the exclusive service area and the square of area 1.0
    service_area = compute_service_area(assigned_facility)

    assert service_area.contains(
        facility_within_square_center.exclusive_service_area
    )
    assert isclose(
        service_area.area
        - facility_within_square_center.exclusive_service_area.area,
        1.0,
    )
