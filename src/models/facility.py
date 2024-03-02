import json
from typing import List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    NonNegativeFloat,
    NonNegativeInt,
    field_serializer,
    field_validator,
)
from shapely import (
    GeometryCollection,
    MultiPolygon,
    Polygon,
    from_geojson,
    to_geojson,
)

from src.models import Client

TYPE_ERROR_MSG = (
    "Not a valid GeoJSON dictionary or valid geometry. "
    "Check the validity of the GeoJSON, or whether the "
    "geometry contains polygons with at least three "
    "distinct points."
)


def _geojson_dict_to_multipolygon(
    geojson_dict: dict,
) -> MultiPolygon:
    """Convert a GeoJSON dictionary to a shapely MultiPolygon"""

    geometry = from_geojson(json.dumps(geojson_dict), on_invalid="ignore")

    if geometry is None or not isinstance(
        geometry, (MultiPolygon, Polygon, GeometryCollection)
    ):
        raise ValueError(TYPE_ERROR_MSG)

    if isinstance(geometry, MultiPolygon):
        return geometry

    if isinstance(geometry, Polygon):
        return MultiPolygon([geometry])

    def _get_inner_polygon(geo):
        if isinstance(geo, Polygon):
            return [geo]
        elif isinstance(geo, MultiPolygon):
            return [p for p in geo.geoms]

        return []

    inner_polygons: List[Polygon] = sum(
        [_get_inner_polygon(geo) for geo in geometry.geoms], []
    )

    if not inner_polygons:
        raise ValueError(TYPE_ERROR_MSG)

    return MultiPolygon(inner_polygons)


def _field_to_multipolygon(field: Union[dict, MultiPolygon]) -> MultiPolygon:
    """Convert a field to a shapely MultiPolygon"""

    if not isinstance(field, (dict, MultiPolygon)):
        raise ValueError(TYPE_ERROR_MSG)

    if isinstance(field, dict):
        return _geojson_dict_to_multipolygon(field)

    return field


def _build_valid_polygon(
    coordinates: List[List[float]],
) -> Union[Polygon, None]:
    """Build valid polygon"""

    valid_coordinates = list(dict.fromkeys(coordinates))
    if len(valid_coordinates) > 2:
        valid_coordinates.append(valid_coordinates[0])
        return Polygon(valid_coordinates)

    return None


def _field_to_valid_multipolygon(
    field: Union[dict, MultiPolygon]
) -> MultiPolygon:
    """Convert a field to a valid MultiPolygon"""

    field_multipolygon = _field_to_multipolygon(field=field)

    if field_multipolygon.is_empty:
        return MultiPolygon()

    valid_polygons = list(
        filter(
            lambda p: p is not None,
            [
                _build_valid_polygon(coordinates=list(polygon.exterior.coords))
                for polygon in field_multipolygon.geoms
            ],
        )
    )

    if not valid_polygons:
        raise ValueError(TYPE_ERROR_MSG)

    return MultiPolygon(valid_polygons)


class Facility(BaseModel):
    """Facility model"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    id: str
    name: str
    lat: float
    lng: float
    min_demand: NonNegativeInt = 0
    max_demand: NonNegativeInt = 0
    exclusive_service_area: MultiPolygon = MultiPolygon()

    @field_serializer("exclusive_service_area")
    def exclusive_service_area_serializer(self, field: MultiPolygon) -> dict:
        return json.loads(to_geojson(field))

    @field_validator("exclusive_service_area", mode="before")
    @classmethod
    def exclusive_service_area_validator(
        cls, field: Union[dict, MultiPolygon]
    ) -> MultiPolygon:
        return _field_to_valid_multipolygon(field=field)


class AssignedFacility(BaseModel):
    """Assigned facility model"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    facility: Facility
    assigned_clients: List[Client]
    expected_demand: NonNegativeFloat = 0.0
    service_area: MultiPolygon = MultiPolygon()
    expected_optimal_tsp_route_distance: NonNegativeFloat = 0.0

    @field_serializer("facility")
    def facility_serializer(self, field: Facility) -> str:
        return field.id

    @field_serializer("assigned_clients")
    def assigned_clients_serializer(self, field: List[Client]) -> List[str]:
        return [client.id for client in field]

    @field_serializer("service_area")
    def service_area_serializer(self, field: MultiPolygon) -> dict:
        return json.loads(to_geojson(field))

    @field_validator("service_area", mode="before")
    @classmethod
    def service_area_validator(
        cls, field: Union[dict, MultiPolygon]
    ) -> MultiPolygon:
        return _field_to_valid_multipolygon(field=field)
