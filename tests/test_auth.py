from unittest.mock import patch


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
