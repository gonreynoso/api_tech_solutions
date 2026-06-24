from unittest.mock import patch


@patch("routes.servicios.Servicio.list_filtered", return_value=[])
def test_list_servicios(mock_list, client):
    resp = client.get("/api/servicios?area=finanzas&estado=activo")
    assert resp.status_code == 200
    mock_list.assert_called_once_with(area="finanzas", estado="activo")


@patch("routes.servicios.Servicio.find_by_id", return_value=None)
def test_get_servicio_not_found(mock_find, client):
    resp = client.get("/api/servicios/999")
    assert resp.status_code == 404


@patch("routes.servicios.Servicio.find_by_plan", return_value=[{"servicio_id": 1}])
def test_servicios_by_plan(mock_find, client):
    resp = client.get("/api/servicios/by-plan/5")
    assert resp.status_code == 200
    assert resp.get_json()["data"] == [{"servicio_id": 1}]


def test_create_servicio_requires_token(client):
    resp = client.post(
        "/api/servicios",
        json={"nombre_servicio": "X", "descripcion": "desc", "area": "finanzas"},
    )
    assert resp.status_code == 401
