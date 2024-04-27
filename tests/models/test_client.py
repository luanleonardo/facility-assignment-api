from math import isclose

from src.models import Client, scale_clients_demands


def test_client_model(clients_data):
    clients = [Client(**data) for data in clients_data]

    assert all(isinstance(client, Client) for client in clients)
    assert all(client.demand > 0 for client in clients)


def test_scale_clients_demands(clients_data):
    clients = [Client(**data) for data in clients_data]

    original_total_demand = sum(client.demand for client in clients)
    expected_new_total_demand = 3 * original_total_demand
    scaled_clients = scale_clients_demands(clients, expected_new_total_demand)
    new_total_demand = sum(client.demand for client in scaled_clients)

    assert isclose(new_total_demand, expected_new_total_demand)
