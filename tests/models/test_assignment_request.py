import humps

from src.models import AssignmentRequest


def test_assignment_request_model(assignment_request_data):
    request_data = humps.decamelize(assignment_request_data)
    assignment_request = AssignmentRequest(**request_data)

    assert isinstance(assignment_request, AssignmentRequest)
