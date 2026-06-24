from unittest.mock import patch


def test_list_casos_requires_token(client):
    resp = client.get("/api/casos")
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.casos.Caso.list_paginated", return_value=([], 0))
def test_list_casos_success(mock_list, mock_decode, client):
    resp = client.get("/api/casos", headers={"Authorization": "Bearer faketoken"})
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.casos.Caso.find_by_id", return_value=None)
def test_get_caso_not_found(mock_find, mock_decode, client):
    resp = client.get("/api/casos/999", headers={"Authorization": "Bearer faketoken"})
    assert resp.status_code == 404


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.casos.Caso.create",
    return_value={"caso_id": 1, "estado_caso": "asignado"},
)
def test_create_caso_success(mock_create, mock_decode, client):
    resp = client.post(
        "/api/casos",
        json={"solicitud_id": 1, "cliente_id": 1, "consultor_id": 2},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["estado_caso"] == "asignado"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_create_caso_missing_fields(mock_decode, client):
    resp = client.post(
        "/api/casos",
        json={"solicitud_id": 1},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.casos.Caso.find_by_id", return_value={"caso_id": 1})
@patch(
    "routes.casos.Caso.update_estado",
    return_value={"caso_id": 1, "estado_caso": "resuelto"},
)
def test_update_caso_success(mock_update, mock_find, mock_decode, client):
    resp = client.put(
        "/api/casos/1",
        json={"estado_caso": "resuelto", "horas_trabajadas": 2},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado_caso"] == "resuelto"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.casos.Caso.find_by_id", return_value={"caso_id": 1})
def test_update_caso_invalid_state(mock_find, mock_decode, client):
    resp = client.put(
        "/api/casos/1",
        json={"estado_caso": "no_existe"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400
