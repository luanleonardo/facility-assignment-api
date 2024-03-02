from copy import deepcopy

from shapely import MultiPolygon, Point, Polygon
from uhull.alpha_shape import get_alpha_shape_polygons

from config import settings
from src.models import AssignedFacility
from src.services import solve_clients_dispersion_problem


def compute_service_area(
    assigned_facility: AssignedFacility,
    alpha=settings.ALPHA_VALUE_CONCAVE_HULL_CONCAVITY,
) -> MultiPolygon:
    """Compute facility service area"""

    facility = deepcopy(assigned_facility.facility)
    assigned_clients = deepcopy(assigned_facility.assigned_clients)

    clients_subset = solve_clients_dispersion_problem(
        clients=assigned_clients,
        subset_size=settings.DISPERSED_CLIENTS_SUBSET_SIZE,
    )

    if not facility.exclusive_service_area.is_empty:
        filtered_clients = [
            client
            for client in assigned_clients
            if not facility.exclusive_service_area.intersects(
                Point(client.lng, client.lat)
            )
        ]
        clients_subset = solve_clients_dispersion_problem(
            clients=filtered_clients,
            subset_size=settings.DISPERSED_CLIENTS_SUBSET_SIZE,
        )

    polygons = list(facility.exclusive_service_area.geoms)
    client_coordinates = list(
        set((client.lng, client.lat) for client in clients_subset)
    )

    if len(client_coordinates) > 3:
        for polygon_coordinates in get_alpha_shape_polygons(
            coordinates_points=client_coordinates,
            alpha=alpha,
        ):
            new_polygon = Polygon(polygon_coordinates)
            if all(not new_polygon.within(polygon) for polygon in polygons):
                polygons.append(new_polygon)

    return MultiPolygon(polygons)
