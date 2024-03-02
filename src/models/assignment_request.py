from enum import IntEnum
from typing import List

from pydantic import BaseModel, PositiveInt, field_validator

from src.models import Client, Facility


class AlgorithmType(IntEnum):
    """Available algorithms for solving the assignment problem"""

    MCF_FORMULATION = 1
    MILP_FORMULATION = 2


class ObjectiveType(IntEnum):
    """Available objective types for the assignment problem"""

    MIN_PROXIMITY = 1
    MIN_TRAVEL_DISTANCE = 2
    MIN_TRAVEL_DURATION = 3


class AssignmentRequest(BaseModel):
    """Assignment request model"""

    total_demand: PositiveInt = 1
    clients: List[Client]
    facilities: List[Facility]
    algorithm: AlgorithmType = AlgorithmType.MCF_FORMULATION
    objective: ObjectiveType = ObjectiveType.MIN_PROXIMITY

    @field_validator("clients", mode="before")
    @classmethod
    def clients_validator(cls, field: List[Client]) -> List[Client]:
        if not field:
            raise ValueError("At least one client is required")

        return field

    @field_validator("facilities", mode="before")
    @classmethod
    def facilities_validator(cls, field: List[Facility]) -> List[Facility]:
        if not field:
            raise ValueError("At least one facility is required")

        return field
