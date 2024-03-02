from enum import IntEnum
from math import inf
from typing import List

from pydantic import BaseModel, NonNegativeFloat

from src.models import AssignedFacility


class SolutionStatus(IntEnum):
    """Status of the solution"""

    INFEASIBLE = 1
    FEASIBLE = 2
    OPTIMAL = 3


class AssignmentSolution(BaseModel):
    """Solution of an assignment problem

    Arguments
    ---------
    objective_value
        Objective value in the returned solution

    assigned_facilities
        A list of facilities and their assigned clients

    solution_status
        Status of the solution

    message
        A message from the solver
    """

    objective_value: NonNegativeFloat = inf
    assigned_facilities: List[AssignedFacility] = []
    solution_status: SolutionStatus = SolutionStatus.INFEASIBLE
    message: str = ""
