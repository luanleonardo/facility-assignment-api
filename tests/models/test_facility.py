from uuid import uuid4

import pytest
from pydantic import ValidationError
from shapely import MultiPolygon

from src.models import AssignedFacility, Client, Facility

INVALID_GEOJSON = [
    None,
    dict(),
    {"type": "FeatureCollection"},
    {"type": "FeatureCollection", "features": [{"geometry": {}}]},
    {
        "type": "FeatureCollection",
        "features": [{"geometry": {"coordinates": []}}],
    },
    {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -60.0134114599588,
                        -3.0916188609801765,
                    ],
                    "type": "Point",
                },
            }
        ],
    },
    {
        "type": "Polygon",
        "coordinates": [[[0.5, 0.75], [0.25, 0.5], [0.5, 0.75]]],
    },
]


def test_facility_model(facilities_data):
    """Test the facility model"""

    facilities = [Facility(**data) for data in facilities_data]
    facilities.append(
        Facility(
            **{
                "id": str(uuid4()),
                "name": "Facility 4",
                "lat": -3.0905742061991424,
                "lng": -59.985171470760335,
                "min_demand": 5,
                "max_demand": 10,
                "exclusive_service_area": MultiPolygon(),
            }
        )
    )
    facilities.append(
        Facility(
            **{
                "id": str(uuid4()),
                "name": "Facility 5",
                "lat": -3.1073436323084693,
                "lng": -60.000580791394405,
                "min_demand": 10,
                "max_demand": 100,
                "exclusive_service_area": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-59.992440783859905, -3.127959087842271],
                            [-59.992440783859905, -3.129075136040683],
                            [-59.99012932088348, -3.129075136040683],
                            [-59.99012932088348, -3.127959087842271],
                            [-59.992440783859905, -3.127959087842271],
                        ]
                    ],
                },
            }
        )
    )
    facilities.append(
        Facility(
            **{
                "id": str(uuid4()),
                "name": "Facility 6",
                "lat": -3.1073436323084693,
                "lng": -60.000580791394405,
                "min_demand": 10,
                "max_demand": 100,
                "exclusive_service_area": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {},
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [
                                            -59.992440783859905,
                                            -3.127959087842271,
                                        ],
                                        [
                                            -59.992440783859905,
                                            -3.129075136040683,
                                        ],
                                        [
                                            -59.99012932088348,
                                            -3.129075136040683,
                                        ],
                                        [
                                            -59.99012932088348,
                                            -3.127959087842271,
                                        ],
                                        [
                                            -59.992440783859905,
                                            -3.127959087842271,
                                        ],
                                    ]
                                ],
                            },
                        }
                    ],
                },
            }
        )
    )

    assert all(isinstance(facility, Facility) for facility in facilities)
    assert all(
        isinstance(facility.exclusive_service_area, MultiPolygon)
        for facility in facilities
    )


def test_exclusive_service_area_serializer():
    """Test the serializer for the exclusive service area of a facility"""

    facility = Facility(
        id=str(uuid4()),
        name="Facility 6",
        lat=-3.0882045980707225,
        lng=-59.96466874582786,
    )

    expected_geojson = {
        "coordinates": [],
        "type": "MultiPolygon",
    }

    assert facility.model_dump()["exclusive_service_area"] == expected_geojson


@pytest.mark.parametrize("geojson", INVALID_GEOJSON)
def test_exclusive_service_area_validator(geojson):
    """Test the validator for the exclusive service area of a facility"""

    facility_data = {
        "id": "7",
        "name": "Facility 7",
        "lat": -3.123,
        "lng": -60.014,
        "min_demand": 5,
        "max_demand": 10,
        "exclusive_service_area": geojson,
    }

    with pytest.raises(
        ValidationError,
        match="Not a valid GeoJSON dictionary or valid geometry.",
    ):
        Facility(**facility_data)


def test_assigned_facility_serialization():
    """Test the serialization of an assigned facility model"""

    facility = Facility(
        id=str(uuid4()),
        name="Facility 8",
        lat=-3.088,
        lng=-59.964,
    )

    client = Client(
        id=str(uuid4()),
        lat=-3.078,
        lng=-59.974,
        demand=10,
    )

    assigned_facility = AssignedFacility(
        facility=facility,
        assigned_clients=[client],
        expected_demand=10,
    )

    assigned_facility_dumped = assigned_facility.model_dump()

    assert assigned_facility_dumped["facility"] == facility.id
    assert assigned_facility_dumped["assigned_clients"] == [client.id]
    assert isinstance(assigned_facility_dumped["service_area"], dict)


@pytest.mark.parametrize("geojson", INVALID_GEOJSON)
def test_assigned_facility_validator(geojson):
    """Test the validator for the service area of an assigned facility"""

    assigned_facility_data = {
        "facility": {
            "id": "1",
            "name": "Facility 9",
            "lat": -3.088,
            "lng": -59.964,
        },
        "assigned_clients": [
            {
                "id": "1",
                "lat": -3.078,
                "lng": -59.974,
                "demand": 10,
            }
        ],
        "expected_demand": 10,
        "service_area": geojson,
    }

    with pytest.raises(
        ValidationError,
        match="Not a valid GeoJSON dictionary or valid geometry.",
    ):
        AssignedFacility(**assigned_facility_data)
