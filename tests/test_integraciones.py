from unittest.mock import patch


def test_list_integraciones_requires_token(client):
    resp = client.get("/api/integraciones")
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.list_paginated",
    return_value=([{"integracion_id": 1, "sistema_externo": "CRMMax"}], 1),
)
def test_list_integraciones_success(mock_list, mock_decode, client):
    resp = client.get(
        "/api/integraciones",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"][0]["sistema_externo"] == "CRMMax"
    assert body["meta"]["total"] == 1


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.list_paginated",
    return_value=([], 0),
)
def test_list_integraciones_with_filters(mock_list, mock_decode, client):
    resp = client.get(
        "/api/integraciones?sistema_externo=CRMMax&estado=confirmado",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["sistema_externo"] == "CRMMax"
    assert mock_list.call_args.kwargs["estado"] == "confirmado"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_list_integraciones_invalid_sistema(mock_decode, client):
    resp = client.get(
        "/api/integraciones?sistema_externo=Inexistente",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_list_integraciones_invalid_estado(mock_decode, client):
    resp = client.get(
        "/api/integraciones?estado=marciano",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.list_paginated",
    return_value=([{"integracion_id": 9, "estado": "error"}], 1),
)
def test_list_errores_filters_by_error_estado(mock_list, mock_decode, client):
    resp = client.get(
        "/api/integraciones/errores",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert mock_list.call_args.kwargs["estado"] == "error"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.find_by_id",
    return_value={"integracion_id": 7, "sistema_externo": "VeriCheck"},
)
def test_get_integracion_success(mock_find, mock_decode, client):
    resp = client.get(
        "/api/integraciones/7",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["integracion_id"] == 7


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.integraciones.IntegracionExterna.find_by_id", return_value=None)
def test_get_integracion_not_found(mock_find, mock_decode, client):
    resp = client.get(
        "/api/integraciones/999",
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 404
