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


@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.clientes.Cliente.create", return_value={"cliente_id": 1, "primer_nombre": "Juan"})
def test_create_cliente_success(mock_create, mock_decode, mock_integracion, client):
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


@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.clientes.Cliente.create", return_value={"cliente_id": 1, "primer_nombre": "Juan"})
def test_create_cliente_syncs_with_crmmax(mock_create, mock_decode, mock_integracion, client):
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
    mock_integracion.assert_called_once()
    assert mock_integracion.call_args.kwargs["sistema_externo"] == "CRMMax"
    assert mock_integracion.call_args.kwargs["estado"] == "confirmado"


@patch(
    "routes.clientes.crmmax.sync_cliente",
    side_effect=ConnectionError("CRMMax no responde"),
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.clientes.Cliente.create", return_value={"cliente_id": 1, "primer_nombre": "Juan"})
def test_create_cliente_crmmax_failure_logs_error(
    mock_create, mock_decode, mock_integracion, mock_sync, client
):
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
    assert mock_integracion.call_args.kwargs["estado"] == "error"


@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 2})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_syncs_with_crmmax(
    mock_find, mock_update, mock_decode, mock_integracion, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    mock_integracion.assert_called_once()
    assert mock_integracion.call_args.kwargs["sistema_externo"] == "CRMMax"
    assert mock_integracion.call_args.kwargs["tipo_evento"] == "actualizacion_cliente"
    assert mock_integracion.call_args.kwargs["estado"] == "confirmado"


@patch(
    "routes.clientes.crmmax.sync_cliente",
    side_effect=ConnectionError("CRMMax no responde"),
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 2})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_crmmax_failure_logs_error(
    mock_find, mock_update, mock_decode, mock_integracion, mock_sync, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert mock_integracion.call_args.kwargs["estado"] == "error"


# ---------- VeriCheck en update (HU5 / HU6) ----------


@patch(
    "routes.clientes.Plan.find_by_id",
    return_value={"plan_id": 2, "nombre_plan": "Premium", "precio": 7900},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 3})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_vericheck_on_plan_change(
    mock_find, mock_update, mock_decode, mock_integracion, mock_plan, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 2,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    vc_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "VeriCheck"
    ]
    assert len(vc_calls) == 1
    assert vc_calls[0].kwargs["tipo_evento"] == "validacion_cambio_critico"
    assert vc_calls[0].kwargs["estado"] == "confirmado"


@patch(
    "routes.clientes.vericheck.validate_identity",
    return_value={"resultado": "rechazada", "motivo": "DNI con formato inválido"},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 3})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_vericheck_blocks_invalid(
    mock_find, mock_decode, mock_integracion, mock_vc, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "INVALIDO",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 403
    assert "bloqueado" in resp.get_json()["message"].lower()


@patch("routes.clientes.vericheck.validate_identity")
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 3})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_no_vericheck_when_no_critical_change(
    mock_find, mock_update, mock_decode, mock_integracion, mock_vc, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Carlos",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    mock_vc.assert_not_called()


# ---------- PagoNet en cambio de plan (HU1 / HU2 / HU9) ----------


@patch(
    "routes.clientes.Plan.find_by_id",
    return_value={"plan_id": 2, "nombre_plan": "Premium", "precio": 7900},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 4})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_factures_pagonet_on_plan_change(
    mock_find, mock_update, mock_decode, mock_integracion, mock_plan, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 2,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    pago_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "PagoNet"
    ]
    assert len(pago_calls) == 1
    assert pago_calls[0].kwargs["tipo_evento"] == "cambio_plan_aprobado"
    assert pago_calls[0].kwargs["estado"] == "confirmado"
    assert pago_calls[0].kwargs["respuesta"]["intento"] == 1


@patch(
    "routes.clientes.pagonet.enviar_facturacion",
    side_effect=[ConnectionError("PagoNet caído"), {"pagonet_id": "p_ok", "status": "accepted"}],
)
@patch(
    "routes.clientes.Plan.find_by_id",
    return_value={"plan_id": 2, "nombre_plan": "Premium", "precio": 7900},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 4})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_pagonet_retries_on_first_failure(
    mock_find, mock_update, mock_decode, mock_integracion, mock_plan, mock_pagonet, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 2,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert mock_pagonet.call_count == 2
    pago_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "PagoNet"
    ]
    assert len(pago_calls) == 1
    assert pago_calls[0].kwargs["estado"] == "confirmado"
    assert pago_calls[0].kwargs["respuesta"]["intento"] == 2


@patch(
    "routes.clientes.pagonet.enviar_facturacion",
    side_effect=ConnectionError("PagoNet caído"),
)
@patch(
    "routes.clientes.Plan.find_by_id",
    return_value={"plan_id": 2, "nombre_plan": "Premium", "precio": 7900},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 4})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_pagonet_all_attempts_fail(
    mock_find, mock_update, mock_decode, mock_integracion, mock_plan, mock_pagonet, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 2,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert mock_pagonet.call_count == 2
    pago_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "PagoNet"
    ]
    assert len(pago_calls) == 1
    assert pago_calls[0].kwargs["estado"] == "error"
    assert pago_calls[0].kwargs["respuesta"]["intentos"] == 2


@patch(
    "routes.clientes.Plan.find_by_id",
    return_value={"plan_id": 2, "nombre_plan": "Premium", "precio": 7900},
)
@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 4})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_notifies_notisys_on_plan_change(
    mock_find, mock_update, mock_decode, mock_integracion, mock_plan, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 2,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    noti_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "NotiSys"
    ]
    assert len(noti_calls) == 1
    assert noti_calls[0].kwargs["tipo_evento"] == "cambio_plan_aprobado"
    assert noti_calls[0].kwargs["estado"] == "confirmado"


@patch("routes.clientes.IntegracionExterna.create", return_value={"integracion_id": 4})
@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.clientes.Cliente.update",
    return_value={"cliente_id": 1, "primer_nombre": "Juan", "apellido": "Lopez"},
)
@patch(
    "routes.clientes.Cliente.find_by_id",
    return_value={"cliente_id": 1, "dni": "12345678", "plan_id": 1},
)
def test_update_cliente_no_pagonet_when_plan_unchanged(
    mock_find, mock_update, mock_decode, mock_integracion, client
):
    resp = client.put(
        "/api/clientes/1",
        json={
            "primer_nombre": "Juan",
            "apellido": "Lopez",
            "dni": "12345678",
            "plan_id": 1,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    pago_calls = [
        c
        for c in mock_integracion.call_args_list
        if c.kwargs["sistema_externo"] == "PagoNet"
    ]
    assert len(pago_calls) == 0
