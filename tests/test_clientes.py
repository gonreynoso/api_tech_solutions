from unittest.mock import patch


@patch("routes.clientes.Cliente.list_paginated", return_value=([], 0))
def test_list_clientes(mock_list, client):
    resp = client.get("/api/clientes")
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


@patch("routes.clientes.Cliente.find_by_id", return_value=None)
def test_get_cliente_not_found(mock_find, client):
    resp = client.get("/api/clientes/999")
    assert resp.status_code == 404


def test_create_cliente_requires_token(client):
    resp = client.post(
        "/api/clientes",
        json={
            "usuario_id": 1,
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "plan_id": 1,
        },
    )
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.clientes.Cliente.create", return_value={"cliente_id": 1, "primer_nombre": "Juan"})
def test_create_cliente_success(mock_create, mock_decode, client):
    resp = client.post(
        "/api/clientes",
        json={
            "usuario_id": 1,
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["primer_nombre"] == "Juan"
