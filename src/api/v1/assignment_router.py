import json
from typing import Any, Dict

import humps
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import ValidationError

from src.models import AssignmentRequest, SolutionStatus
from src.services import solve_facility_assignment

router = APIRouter()


@router.post("/solve-assignment")
async def solve_assignment(request_json: Dict[str, Any]):
    try:
        # Convert request JSON keys to snake_case
        snake_case_request_json = humps.decamelize(request_json)
        assignment_request = AssignmentRequest(**snake_case_request_json)
        assignment_solution = solve_facility_assignment(assignment_request)

        if assignment_solution.solution_status == SolutionStatus.INFEASIBLE:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=assignment_solution.message,
            )

        # Convert the result to camelCase
        camel_case_solution = humps.camelize(assignment_solution.model_dump())

        # Create a Response instance with the data, status_code, and return it
        return Response(
            content=json.dumps(camel_case_solution),
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
    except ValidationError as e:
        error_messages = [
            {
                "error": error["msg"],
                "path_error": "->".join([str(i) for i in error["loc"]]),
                "input": error["input"],
            }
            for error in e.errors()
        ]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"{e.error_count()} fields with validation error",
                "fields": error_messages,
            },
        )
