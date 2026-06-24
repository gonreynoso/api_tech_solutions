from unittest.mock import patch


def test_list_usuarios_requires_token(client):
    resp = client.get("/api/usuarios")
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.usuarios.Usuario.list_all",
    return_value=[{"usuario_id": 1, "email": "a@b.com", "rol": "administrador"}],
)
def test_list_usuarios_success(mock_list, mock_decode, client):
    resp = client.get("/api/usuarios", headers={"Authorization": "Bearer faketoken"})
    assert resp.status_code == 200
    body = resp.get_json()["data"]
    assert body[0]["email"] == "a@b.com"
    assert "contraseña" not in body[0]
    assert "token_jwt" not in body[0]


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.usuarios.Usuario.find_public_by_id", return_value=None)
def test_get_usuario_not_found(mock_find, mock_decode, client):
    resp = client.get("/api/usuarios/999", headers={"Authorization": "Bearer faketoken"})
    assert resp.status_code == 404
