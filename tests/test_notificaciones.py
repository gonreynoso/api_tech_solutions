from unittest.mock import patch


def test_list_notificaciones_requires_token(client):
    resp = client.get("/api/notificaciones?usuario_id=1")
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_list_notificaciones_missing_usuario_id(mock_decode, client):
    resp = client.get(
        "/api/notificaciones", headers={"Authorization": "Bearer faketoken"}
    )
    assert resp.status_code == 400


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.notificaciones.Notificacion.list_paginated", return_value=([], 0))
def test_list_notificaciones_success(mock_list, mock_decode, client):
    resp = client.get(
        "/api/notificaciones?usuario_id=1",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.notificaciones.Notificacion.create",
    return_value={"notificacion_id": 1, "leida": False},
)
def test_create_notificacion_success(mock_create, mock_decode, client):
    resp = client.post(
        "/api/notificaciones",
        json={
            "usuario_id": 1,
            "tipo": "sistema",
            "asunto": "Hola",
            "contenido": "Bienvenido",
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["leida"] is False


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.notificaciones.Notificacion.find_by_id", return_value=None)
def test_mark_notificacion_leida_not_found(mock_find, mock_decode, client):
    resp = client.put(
        "/api/notificaciones/999/leida",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 404


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.notificaciones.Notificacion.find_by_id", return_value={"notificacion_id": 1})
@patch(
    "routes.notificaciones.Notificacion.mark_as_read",
    return_value={"notificacion_id": 1, "leida": True},
)
def test_mark_notificacion_leida_success(mock_mark, mock_find, mock_decode, client):
    resp = client.put(
        "/api/notificaciones/1/leida",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["leida"] is True
