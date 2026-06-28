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


# ---------- POST /simular (página demo Equipo 5) ----------


def test_simular_requires_token(client):
    resp = client.post(
        "/api/integraciones/simular",
        json={"sistema_externo": "CRMMax", "tipo_evento": "sincronizacion_cliente"},
    )
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.create",
    return_value={"integracion_id": 10, "estado": "confirmado"},
)
def test_simular_success(mock_create, mock_decode, client):
    resp = client.post(
        "/api/integraciones/simular",
        json={
            "sistema_externo": "CRMMax",
            "tipo_evento": "sincronizacion_cliente",
            "cliente_id": 7,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert mock_create.call_args.kwargs["sistema_externo"] == "CRMMax"
    assert mock_create.call_args.kwargs["tipo_evento"] == "sincronizacion_cliente"
    assert mock_create.call_args.kwargs["estado"] == "confirmado"
    assert mock_create.call_args.kwargs["registro_id"] == 7
    assert mock_create.call_args.kwargs["respuesta"]["simulacion"] is True


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.integraciones.IntegracionExterna.create",
    return_value={"integracion_id": 11, "estado": "error"},
)
def test_simular_forzar_error(mock_create, mock_decode, client):
    resp = client.post(
        "/api/integraciones/simular",
        json={
            "sistema_externo": "PagoNet",
            "tipo_evento": "envio_facturacion",
            "forzar_error": True,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert mock_create.call_args.kwargs["estado"] == "error"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_simular_invalid_sistema(mock_decode, client):
    resp = client.post(
        "/api/integraciones/simular",
        json={"sistema_externo": "Inexistente", "tipo_evento": "x"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_simular_missing_fields(mock_decode, client):
    resp = client.post(
        "/api/integraciones/simular",
        json={"sistema_externo": "CRMMax"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


# ---------- Página demo ----------


def test_demo_index_html(client):
    resp = client.get("/eq5-demo")
    assert resp.status_code == 200
    assert b"Equipo 5" in resp.data
