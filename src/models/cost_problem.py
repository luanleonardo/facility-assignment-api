from enum import IntEnum
from typing import List, Union

from pydantic import BaseModel, PositiveInt, field_validator

from config import settings
from src.models import Client, Facility, ObjectiveType


class CostType(IntEnum):
    """Available cost types for the cost problem"""

    SPHERICAL_DISTANCE = 1
    OSRM_DISTANCE = 2
    OSRM_DURATION = 3


OBJECTIVE_TYPE_MAPPING = {
    ObjectiveType.MIN_PROXIMITY: CostType.SPHERICAL_DISTANCE,
    ObjectiveType.MIN_TRAVEL_DISTANCE: CostType.OSRM_DISTANCE,
    ObjectiveType.MIN_TRAVEL_DURATION: CostType.OSRM_DURATION,
}


class CostProblem(BaseModel):
    """Cost problem model"""

    clients: List[Client]
    facilities: List[Facility]
    cost_type: Union[CostType, ObjectiveType] = CostType.SPHERICAL_DISTANCE
    osrm_server_address: str = settings.OSRM_SERVER_ADDRESS
    osrm_batch_size: PositiveInt = settings.OSRM_BATCH_SIZE

    @field_validator("cost_type", mode="before")
    @classmethod
    def cost_type_validator(
        cls, field: Union[CostType, ObjectiveType]
    ) -> CostType:
        if not isinstance(field, (CostType, ObjectiveType)):
            raise ValueError(
                f"Cost problem type {field} "
                f"is not a valid assignment objective"
            )

        if isinstance(field, CostType):
            return field

        return OBJECTIVE_TYPE_MAPPING[field]
