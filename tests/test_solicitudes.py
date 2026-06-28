from unittest.mock import patch


def test_list_solicitudes_requires_token(client):
    resp = client.get("/api/solicitudes")
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.solicitudes.Solicitud.list_paginated", return_value=([], 0))
def test_list_solicitudes_success(mock_list, mock_decode, client):
    resp = client.get(
        "/api/solicitudes", headers={"Authorization": "Bearer faketoken"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.solicitudes.Solicitud.find_by_id", return_value=None)
def test_get_solicitud_not_found(mock_find, mock_decode, client):
    resp = client.get(
        "/api/solicitudes/999", headers={"Authorization": "Bearer faketoken"}
    )
    assert resp.status_code == 404


@patch("routes.solicitudes.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.solicitudes.Solicitud.create",
    return_value={"solicitud_id": 1, "cliente_id": 1, "estado_solicitud": "pendiente"},
)
def test_create_solicitud_success(mock_create, mock_decode, mock_integracion, client):
    resp = client.post(
        "/api/solicitudes",
        json={"cliente_id": 1, "servicio_id": 1, "descripcion": "Necesito ayuda"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["estado_solicitud"] == "pendiente"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
def test_create_solicitud_missing_fields(mock_decode, client):
    resp = client.post(
        "/api/solicitudes",
        json={"cliente_id": 1},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400


@patch("routes.solicitudes.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.solicitudes.Solicitud.find_by_id", return_value={"solicitud_id": 1})
@patch(
    "routes.solicitudes.Solicitud.update_estado",
    return_value={"solicitud_id": 1, "cliente_id": 1, "estado_solicitud": "aprobada"},
)
def test_update_estado_solicitud_success(
    mock_update, mock_find, mock_decode, mock_integracion, client
):
    resp = client.put(
        "/api/solicitudes/1/estado",
        json={"estado_solicitud": "aprobada"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado_solicitud"] == "aprobada"


# ---------- NotiSys en solicitudes (HU7 / HU8) ----------


@patch("routes.solicitudes.IntegracionExterna.create", return_value={"integracion_id": 5})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.solicitudes.Solicitud.create",
    return_value={"solicitud_id": 1, "cliente_id": 1, "estado_solicitud": "pendiente"},
)
def test_create_solicitud_notifies_notisys(
    mock_create, mock_decode, mock_integracion, client
):
    resp = client.post(
        "/api/solicitudes",
        json={"cliente_id": 1, "servicio_id": 1, "descripcion": "Necesito ayuda"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    mock_integracion.assert_called_once()
    assert mock_integracion.call_args.kwargs["sistema_externo"] == "NotiSys"
    assert mock_integracion.call_args.kwargs["tipo_evento"] == "solicitud_creada"
    assert mock_integracion.call_args.kwargs["estado"] == "confirmado"


@patch(
    "routes.solicitudes.notisys.enviar_notificacion",
    side_effect=ConnectionError("NotiSys no responde"),
)
@patch("routes.solicitudes.IntegracionExterna.create", return_value={"integracion_id": 5})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.solicitudes.Solicitud.create",
    return_value={"solicitud_id": 1, "cliente_id": 1, "estado_solicitud": "pendiente"},
)
def test_create_solicitud_notisys_failure_logs_error(
    mock_create, mock_decode, mock_integracion, mock_send, client
):
    resp = client.post(
        "/api/solicitudes",
        json={"cliente_id": 1, "servicio_id": 1, "descripcion": "Necesito ayuda"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert mock_integracion.call_args.kwargs["estado"] == "error"


@patch("routes.solicitudes.IntegracionExterna.create", return_value={"integracion_id": 6})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.solicitudes.Solicitud.find_by_id", return_value={"solicitud_id": 1})
@patch(
    "routes.solicitudes.Solicitud.update_estado",
    return_value={"solicitud_id": 1, "cliente_id": 1, "estado_solicitud": "aprobada"},
)
def test_update_estado_solicitud_notifies_notisys(
    mock_update, mock_find, mock_decode, mock_integracion, client
):
    resp = client.put(
        "/api/solicitudes/1/estado",
        json={"estado_solicitud": "aprobada"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    mock_integracion.assert_called_once()
    assert mock_integracion.call_args.kwargs["sistema_externo"] == "NotiSys"
    assert mock_integracion.call_args.kwargs["tipo_evento"] == "cambio_estado_solicitud"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.solicitudes.Solicitud.find_by_id", return_value={"solicitud_id": 1})
def test_update_estado_solicitud_invalid_state(mock_find, mock_decode, client):
    resp = client.put(
        "/api/solicitudes/1/estado",
        json={"estado_solicitud": "no_existe"},
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 400
