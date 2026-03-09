"""Tests for vehicle endpoints."""

import pytest


class TestVehicleCRUD:
    """Test vehicle CRUD operations."""

    def test_create_vehicle(self, client, sample_vehicle):
        response = client.post("/api/v1/vehicles/", json=sample_vehicle)
        assert response.status_code == 201
        data = response.json()
        assert data["brand"] == "Toyota"
        assert data["model"] == "Corolla"
        assert data["license_plate"] == "ABC1D23"
        assert "id" in data

    def test_create_duplicate_plate(self, client, sample_vehicle):
        client.post("/api/v1/vehicles/", json=sample_vehicle)
        response = client.post("/api/v1/vehicles/", json=sample_vehicle)
        assert response.status_code == 409

    def test_list_vehicles(self, client, sample_vehicle, sample_vehicle_suv):
        client.post("/api/v1/vehicles/", json=sample_vehicle)
        client.post("/api/v1/vehicles/", json=sample_vehicle_suv)
        response = client.get("/api/v1/vehicles/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_vehicles_by_category(self, client, sample_vehicle, sample_vehicle_suv):
        client.post("/api/v1/vehicles/", json=sample_vehicle)
        client.post("/api/v1/vehicles/", json=sample_vehicle_suv)
        response = client.get("/api/v1/vehicles/?category=suv")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "suv"

    def test_get_vehicle(self, client, sample_vehicle):
        create_resp = client.post("/api/v1/vehicles/", json=sample_vehicle)
        vehicle_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 200
        assert response.json()["id"] == vehicle_id

    def test_get_vehicle_not_found(self, client):
        response = client.get("/api/v1/vehicles/nonexistent")
        assert response.status_code == 404

    def test_update_vehicle(self, client, sample_vehicle):
        create_resp = client.post("/api/v1/vehicles/", json=sample_vehicle)
        vehicle_id = create_resp.json()["id"]
        response = client.patch(
            f"/api/v1/vehicles/{vehicle_id}",
            json={"daily_rate": 179.90, "mileage": 20000},
        )
        assert response.status_code == 200
        assert response.json()["daily_rate"] == 179.90
        assert response.json()["mileage"] == 20000

    def test_delete_vehicle(self, client, sample_vehicle):
        create_resp = client.post("/api/v1/vehicles/", json=sample_vehicle)
        vehicle_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 204

        response = client.get(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 404
