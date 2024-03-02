from typing import Dict, List

from ortools.graph.python import min_cost_flow
from shapely import Point

from config import settings
from src.models import (
    AssignedFacility,
    AssignmentProblem,
    AssignmentSolution,
    SolutionStatus,
)
from src.services import (
    evaluate_assigned_facilities,
    scale_assignment_problem_parameters,
)


def _build_mcf_model(
    assignment_problem: AssignmentProblem,
) -> min_cost_flow.SimpleMinCostFlow:
    """Build the Min Cost Flow model"""

    # Create model for the problem
    model = min_cost_flow.SimpleMinCostFlow()

    # Scale problem parameters to become integer
    scaled_clients, scaled_facilities, scaled_cost_matrix = (
        scale_assignment_problem_parameters(
            assignment_problem=assignment_problem,
            scale_factor=settings.MCF_SCALE_FACTOR,
        )
    )

    # Define the directed graph for the flow.
    # Each client has a supply equal to its demand.
    supplies = [int(client.demand) for client in scaled_clients]
    total_clients_supplies = sum(supplies)

    # Get the demands for each facility.
    num_clients = len(scaled_clients)
    num_facilities = len(scaled_facilities)
    terminal_node = num_clients + num_facilities
    total_facilities_demand = 0

    for i in range(num_clients, terminal_node):
        facility_demand = scaled_facilities[i - num_clients].min_demand
        total_facilities_demand += facility_demand
        supplies.append(-facility_demand)

    # The total demand defined for the terminal node must be the difference
    # between supplies minus the sum of demands from all facilities
    supplies.append(-(total_clients_supplies - total_facilities_demand))

    # Add supply/demand nodes to the graph.
    for i, value in enumerate(supplies):
        model.set_node_supply(i, value)

    # Add arcs from clients to facilities
    exclusive_service_areas = [
        (i, facility.exclusive_service_area)
        for i, facility in enumerate(scaled_facilities)
        if not facility.exclusive_service_area.is_empty
    ]
    for j, client in enumerate(scaled_clients):
        areas_containing_client = [
            i
            for i, area in exclusive_service_areas
            if area.intersects(Point(client.lng, client.lat))
        ]
        if len(areas_containing_client) > 1:
            intersecting_facilities = [
                scaled_facilities[i].name for i in areas_containing_client
            ]
            raise ValueError(
                "Impossible solve the problem! "
                "There is an intersection in the exclusive service areas "
                f"of the following facilities: {intersecting_facilities}. "
                "The following coordinates belongs to this intersection: "
                f"{(client.lat, client.lng)}."
            )
        if len(areas_containing_client) == 1:
            i = num_clients + areas_containing_client[0]
            cost = scaled_cost_matrix[i - num_clients][j]
            model.add_arc_with_capacity_and_unit_cost(
                tail=j, head=i, capacity=supplies[j], unit_cost=cost
            )
            continue
        for i in range(num_clients, terminal_node):
            cost = scaled_cost_matrix[i - num_clients][j]
            model.add_arc_with_capacity_and_unit_cost(
                tail=j, head=i, capacity=supplies[j], unit_cost=cost
            )

    # Add arc from facilities to terminal node
    for i in range(num_clients, terminal_node):
        max_demand = scaled_facilities[i - num_clients].max_demand
        capacity = max_demand or total_clients_supplies
        if supplies[i] < 0:
            capacity += supplies[i]
        model.add_arc_with_capacity_and_unit_cost(
            tail=i, head=terminal_node, capacity=capacity, unit_cost=0
        )

    return model


def solve_flow_assignment_formulation(
    assignment_problem: AssignmentProblem,
) -> AssignmentSolution:
    """Solve assignment problem via Min Cost Flow"""

    # Build the Min Cost Flow model
    try:
        model = _build_mcf_model(assignment_problem)
    except ValueError as e:
        return AssignmentSolution(
            solution_status=SolutionStatus.INFEASIBLE,
            message=str(e),
        )

    # Solve the Min Cost Flow model
    status = model.solve()

    # If the problem is feasible, get the assignments
    if status == model.OPTIMAL:
        num_facilities = len(assignment_problem.facilities)
        num_clients = len(assignment_problem.clients)
        terminal_node = num_clients + num_facilities
        assignments: Dict[int, List[int]] = {
            i: [] for i in range(num_facilities)
        }

        for arc in range(model.num_arcs()):
            if model.head(arc) != terminal_node and model.flow(arc) > 0:
                assignments[model.head(arc) - num_clients].append(
                    model.tail(arc)
                )

        assigned_facilities = [
            AssignedFacility(
                facility=facility,
                assigned_clients=[
                    assignment_problem.clients[j] for j in assignments[i]
                ],
            )
            for i, facility in enumerate(assignment_problem.facilities)
        ]

        # Evaluate assigned facilities
        evaluated_assigned_facilities = evaluate_assigned_facilities(
            assigned_facilities
        )

        return AssignmentSolution(
            objective_value=round(
                model.optimal_cost() / (settings.MCF_SCALE_FACTOR**2)
            ),
            assigned_facilities=evaluated_assigned_facilities,
            solution_status=SolutionStatus.OPTIMAL,
            message="Optimal solution found",
        )

    return AssignmentSolution(message="No optimal solution found")
