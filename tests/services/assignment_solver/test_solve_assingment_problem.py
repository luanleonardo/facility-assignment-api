import pytest

from src.models import (
    AlgorithmType,
    AssignmentProblem,
    AssignmentRequest,
    Client,
    CostProblem,
    Facility,
    SolutionStatus,
)
from src.services import (
    compute_cost_matrix,
    solve_facility_assignment,
    solve_flow_assignment_formulation,
    solve_milp_assignment_formulation,
)

SOLVER_MAPPING = {
    AlgorithmType.MCF_FORMULATION: solve_flow_assignment_formulation,
    AlgorithmType.MILP_FORMULATION: solve_milp_assignment_formulation,
}


@pytest.fixture
def clients():
    coordinates = [
        (0.75, 0.75),
        (0.5, 1.5),
        (1.5, 1.5),
        (1.5, 0.5),
        (2.5, 3.5),
        (2.5, 2.5),
        (3.5, 2.5),
        (3.5, 3.5),
    ]

    return [
        Client(id=str(i), lat=lat, lng=lng)
        for i, (lat, lng) in enumerate(coordinates, start=1)
    ]


@pytest.fixture
def facilities():
    facilities_data = [
        {"id": "1", "name": "FC1", "lat": 1.0, "lng": 1.0, "max_demand": 1},
        {"id": "2", "name": "FC2", "lat": 3.0, "lng": 3.0},
    ]

    return [Facility(**data) for data in facilities_data]


@pytest.fixture
def facilities_with_exclusive_area():
    exclusive_area_1 = {
        "coordinates": [
            [
                [2.25, 2.25],
                [2.75, 2.25],
                [2.75, 2.75],
                [2.25, 2.75],
                [2.25, 2.25],
            ]
        ],
        "type": "Polygon",
    }
    exclusive_area_2 = {
        "coordinates": [
            [
                [1.25, 1.25],
                [1.75, 1.25],
                [1.75, 1.75],
                [1.25, 1.75],
                [1.25, 1.25],
            ]
        ],
        "type": "Polygon",
    }

    facilities_data = [
        {
            "id": "1",
            "name": "FC1",
            "lat": 1.0,
            "lng": 1.0,
            "min_demand": 3,
            "exclusive_service_area": exclusive_area_1,
        },
        {
            "id": "2",
            "name": "FC2",
            "lat": 3.0,
            "lng": 3.0,
            "min_demand": 3,
            "max_demand": 6,
            "exclusive_service_area": exclusive_area_2,
        },
    ]

    return [Facility(**data) for data in facilities_data]


@pytest.fixture
def facilities_with_intersecting_exclusive_area():
    exclusive_area_1 = {
        "coordinates": [
            [
                [2.25, 2.25],
                [2.75, 2.25],
                [2.75, 2.75],
                [2.25, 2.75],
                [2.25, 2.25],
            ]
        ],
        "type": "Polygon",
    }

    facilities_data = [
        {
            "id": "1",
            "name": "FC1",
            "lat": 1.0,
            "lng": 1.0,
            "min_demand": 3,
            "exclusive_service_area": exclusive_area_1,
        },
        {
            "id": "2",
            "name": "FC2",
            "lat": 3.0,
            "lng": 3.0,
            "min_demand": 3,
            "max_demand": 6,
            "exclusive_service_area": exclusive_area_1,
        },
    ]

    return [Facility(**data) for data in facilities_data]


@pytest.fixture(
    params=[AlgorithmType.MCF_FORMULATION, AlgorithmType.MILP_FORMULATION]
)
def assignment_problem(request, clients, facilities):
    cost_problem = CostProblem(clients=clients, facilities=facilities)
    cost_matrix = compute_cost_matrix(cost_problem)
    return AssignmentProblem(
        clients=clients,
        facilities=facilities,
        cost_matrix=cost_matrix,
        algorithm=request.param,
    )


@pytest.fixture(
    params=[AlgorithmType.MCF_FORMULATION, AlgorithmType.MILP_FORMULATION]
)
def assignment_problem_with_exclusive_areas(
    request, clients, facilities_with_exclusive_area
):
    cost_problem = CostProblem(
        clients=clients, facilities=facilities_with_exclusive_area
    )
    cost_matrix = compute_cost_matrix(cost_problem)
    return AssignmentProblem(
        clients=clients,
        facilities=facilities_with_exclusive_area,
        cost_matrix=cost_matrix,
        algorithm=request.param,
    )


@pytest.fixture(
    params=[AlgorithmType.MCF_FORMULATION, AlgorithmType.MILP_FORMULATION]
)
def assignment_problem_with_intersecting_exclusive_areas(
    request, clients, facilities_with_intersecting_exclusive_area
):
    cost_problem = CostProblem(
        clients=clients, facilities=facilities_with_intersecting_exclusive_area
    )
    cost_matrix = compute_cost_matrix(cost_problem)
    return AssignmentProblem(
        clients=clients,
        facilities=facilities_with_intersecting_exclusive_area,
        cost_matrix=cost_matrix,
        algorithm=request.param,
    )


def test_optimal_assigment_problem(assignment_problem):

    assignment_solution = SOLVER_MAPPING[assignment_problem.algorithm](
        assignment_problem
    )

    assert assignment_solution.solution_status == SolutionStatus.OPTIMAL


def test_optimal_assigment_problem_with_exclusive_areas(
    assignment_problem_with_exclusive_areas,
):

    assignment_solution = SOLVER_MAPPING[
        assignment_problem_with_exclusive_areas.algorithm
    ](assignment_problem_with_exclusive_areas)

    assert assignment_solution.solution_status == SolutionStatus.OPTIMAL


def test_optimal_assigment_problem_with_intersecting_exclusive_areas(
    assignment_problem_with_intersecting_exclusive_areas,
):
    solution = SOLVER_MAPPING[
        assignment_problem_with_intersecting_exclusive_areas.algorithm
    ](assignment_problem_with_intersecting_exclusive_areas)

    assert solution.solution_status == SolutionStatus.INFEASIBLE
    assert "Impossible solve the problem!" in solution.message


def test_infeasible_assignment_problem(assignment_problem):
    """
    When the facilities cannot handle total load, the problem is infeasible
    """
    assignment_problem.facilities[0].max_demand = 1
    assignment_problem.facilities[1].max_demand = 1

    assignment_solution = SOLVER_MAPPING[assignment_problem.algorithm](
        assignment_problem
    )

    assert assignment_solution.solution_status == SolutionStatus.INFEASIBLE


def test_assigment_problem_assigns_all_clients(assignment_problem):
    assignment_solution = SOLVER_MAPPING[assignment_problem.algorithm](
        assignment_problem
    )

    input_clients = set(
        frozenset(client) for client in assignment_problem.clients
    )

    output_clients = set(
        frozenset(client)
        for facility_assignments in assignment_solution.assigned_facilities
        for client in facility_assignments.assigned_clients
    )

    assert input_clients == output_clients


def test_assigment_problem_respects_max_demand(assignment_problem):
    total_demand = len(assignment_problem.clients)

    assignment_solution = SOLVER_MAPPING[assignment_problem.algorithm](
        assignment_problem
    )

    client_demands = [
        sum(client.demand for client in facility_assignments.assigned_clients)
        for facility_assignments in assignment_solution.assigned_facilities
    ]

    facility_max_demands = [
        facility_assignments.facility.max_demand or total_demand
        for facility_assignments in assignment_solution.assigned_facilities
    ]

    assert all(
        client_demand <= facility_max_demand
        for client_demand, facility_max_demand in zip(
            client_demands, facility_max_demands
        )
    )


@pytest.mark.parametrize(
    "algorithm_type",
    [AlgorithmType.MCF_FORMULATION, AlgorithmType.MILP_FORMULATION],
)
def test_solve_facility_assignment(clients, facilities, algorithm_type):

    request = AssignmentRequest(
        total_demand=sum(client.demand for client in clients),
        clients=clients,
        facilities=facilities,
        algorithm=algorithm_type,
    )

    assignment_solution = solve_facility_assignment(request)

    assert assignment_solution.solution_status == SolutionStatus.OPTIMAL
