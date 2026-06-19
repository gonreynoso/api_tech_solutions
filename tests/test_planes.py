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
