from unittest.mock import patch


def test_register_missing_fields(client):
    resp = client.post("/api/auth/register", json={})
    assert resp.status_code == 400


def test_register_invalid_email(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "secret123",
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "plan_id": 1,
        },
    )
    assert resp.status_code == 400


@patch("routes.auth.Usuario.find_by_email", return_value={"usuario_id": 1})
def test_register_email_already_exists(mock_find, client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@b.com",
            "password": "secret123",
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "plan_id": 1,
        },
    )
    assert resp.status_code == 409


@patch("routes.auth.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("routes.auth.Usuario.find_by_email", return_value=None)
def test_register_vericheck_rejects(mock_find, mock_integracion, client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@b.com",
            "password": "secret123",
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "no-es-un-dni",
            "plan_id": 1,
        },
    )
    assert resp.status_code == 401
    assert mock_integracion.call_args.kwargs["estado"] == "error"


@patch("routes.auth.Usuario.update_token")
@patch(
    "routes.auth.Cliente.create",
    return_value={"cliente_id": 1, "primer_nombre": "Juan"},
)
@patch(
    "routes.auth.Usuario.create",
    return_value={"usuario_id": 1, "email": "a@b.com", "rol": "cliente"},
)
@patch("routes.auth.IntegracionExterna.create", return_value={"integracion_id": 1})
@patch("routes.auth.Usuario.find_by_email", return_value=None)
def test_register_success(
    mock_find, mock_integracion, mock_usuario_create, mock_cliente_create, mock_update, client
):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@b.com",
            "password": "secret123",
            "primer_nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "plan_id": 1,
        },
    )
    body = resp.get_json()
    assert resp.status_code == 201
    assert "access_token" in body["data"]
    assert body["data"]["cliente"]["primer_nombre"] == "Juan"
    assert mock_integracion.call_args.kwargs["sistema_externo"] == "VeriCheck"
    assert mock_integracion.call_args.kwargs["estado"] == "confirmado"


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_login_invalid_email(client):
    resp = client.post(
        "/api/auth/login", json={"email": "not-an-email", "password": "secret"}
    )
    assert resp.status_code == 400


@patch("routes.auth.Usuario.find_by_email", return_value=None)
def test_login_invalid_credentials(mock_find, client):
    resp = client.post(
        "/api/auth/login", json={"email": "a@b.com", "password": "secret"}
    )
    assert resp.status_code == 401
    assert resp.get_json()["success"] is False


@patch("routes.auth.Usuario.update_token")
@patch("routes.auth.check_password_hash", return_value=True)
@patch(
    "routes.auth.Usuario.find_by_email",
    return_value={
        "usuario_id": 1,
        "email": "a@b.com",
        "contraseña": "hashed",
        "rol": "cliente",
    },
)
def test_login_success(mock_find, mock_check, mock_update, client):
    resp = client.post(
        "/api/auth/login", json={"email": "a@b.com", "password": "secret"}
    )
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["user"]["rol"] == "cliente"
