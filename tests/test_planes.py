from unittest.mock import patch


@patch("routes.planes.Plan.list_all", return_value=[{"plan_id": 1, "nombre_plan": "Basico"}])
def test_list_planes(mock_list, client):
    resp = client.get("/api/planes")
    assert resp.status_code == 200
    assert resp.get_json()["data"] == [{"plan_id": 1, "nombre_plan": "Basico"}]


@patch("routes.planes.Plan.find_by_id", return_value=None)
def test_get_plan_not_found(mock_find, client):
    resp = client.get("/api/planes/999")
    assert resp.status_code == 404


@patch("routes.planes.Plan.find_by_id", return_value={"plan_id": 1, "nombre_plan": "Basico"})
def test_get_plan_found(mock_find, client):
    resp = client.get("/api/planes/1")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["nombre_plan"] == "Basico"


def test_create_plan_requires_token(client):
    resp = client.post(
        "/api/planes",
        json={
            "nombre_plan": "Básico",
            "precio": 99.99,
            "creditos": 30,
            "tiempo_respuesta": 48,
        },
    )
    assert resp.status_code == 401


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch(
    "routes.planes.Plan.create",
    return_value={"plan_id": 1, "nombre_plan": "Básico"},
)
def test_create_plan_success(mock_create, mock_decode, client):
    resp = client.post(
        "/api/planes",
        json={
            "nombre_plan": "Básico",
            "precio": 99.99,
            "creditos": 30,
            "tiempo_respuesta": 48,
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["nombre_plan"] == "Básico"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.planes.Plan.find_by_id", return_value={"plan_id": 1})
@patch(
    "routes.planes.Plan.update",
    return_value={"plan_id": 1, "estado_plan": "discontinuado"},
)
def test_update_plan_success(mock_update, mock_find, mock_decode, client):
    resp = client.put(
        "/api/planes/1",
        json={
            "nombre_plan": "Básico",
            "precio": 99.99,
            "creditos": 30,
            "tiempo_respuesta": 48,
            "estado_plan": "discontinuado",
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado_plan"] == "discontinuado"


@patch("middleware.auth.jwt.decode", return_value={"user_id": 1, "email": "a@b.com"})
@patch("routes.planes.Plan.find_by_id", return_value=None)
def test_update_plan_not_found(mock_find, mock_decode, client):
    resp = client.put(
        "/api/planes/999",
        json={
            "nombre_plan": "Básico",
            "precio": 99.99,
            "creditos": 30,
            "tiempo_respuesta": 48,
            "estado_plan": "activo",
        },
        headers={"Authorization": "Bearer faketoken"},
    )
    assert resp.status_code == 404
