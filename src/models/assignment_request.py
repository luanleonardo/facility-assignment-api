from enum import IntEnum
from typing import List

from pydantic import BaseModel, Field, PositiveInt

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
    clients: List[Client] = Field(min_length=1)
    facilities: List[Facility] = Field(min_length=1)
    algorithm: AlgorithmType = AlgorithmType.MCF_FORMULATION
    objective: ObjectiveType = ObjectiveType.MIN_PROXIMITY
