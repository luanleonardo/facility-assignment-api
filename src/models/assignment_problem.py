from typing import List

import numpy as np
from pydantic import BaseModel, ConfigDict

from src.models import AlgorithmType, Client, Facility


class AssignmentProblem(BaseModel):
    """Assignment problem model"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    clients: List[Client]
    facilities: List[Facility]
    cost_matrix: np.ndarray
    algorithm: AlgorithmType = AlgorithmType.MCF_FORMULATION
    solver_time_limit_seconds: int = 80
