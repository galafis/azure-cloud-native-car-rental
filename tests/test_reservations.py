"""Tests for reservation endpoints."""

from datetime import date, timedelta

import pytest


class TestReservations:
    """Test reservation operations."""

    def _create_vehicle(self, client, sample_vehicle):
        resp = client.post("/api/v1/vehicles/", json=sample_vehicle)
        return resp.json()["id"]

    def _make_reservation(self, client, vehicle_id, days_ahead=1, duration=3):
        start = date.today() + timedelta(days=days_ahead)
        end = start + timedelta(days=duration)
        return client.post(
            "/api/v1/reservations/",
            json={
                "vehicle_id": vehicle_id,
                "customer_name": "Joao Silva",
                "customer_email": "joao@example.com",
                "customer_document": "12345678901",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )

    def test_create_reservation(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        response = self._make_reservation(client, vehicle_id)
        assert response.status_code == 201
        data = response.json()
        assert data["reservation"]["vehicle_id"] == vehicle_id
        assert data["reservation"]["status"] == "pending"
        assert data["reservation"]["total_amount"] > 0

    def test_create_reservation_vehicle_not_found(self, client):
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=3)
        response = client.post(
            "/api/v1/reservations/",
            json={
                "vehicle_id": "nonexistent",
                "customer_name": "Joao Silva",
                "customer_email": "joao@example.com",
                "customer_document": "12345678901",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_create_reservation_date_conflict(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        self._make_reservation(client, vehicle_id, days_ahead=1, duration=5)
        response = self._make_reservation(client, vehicle_id, days_ahead=2, duration=3)
        assert response.status_code == 400

    def test_list_reservations(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        self._make_reservation(client, vehicle_id, days_ahead=1, duration=3)
        self._make_reservation(client, vehicle_id, days_ahead=10, duration=3)

        response = client.get("/api/v1/reservations/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_cancel_reservation(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        create_resp = self._make_reservation(client, vehicle_id)
        res_id = create_resp.json()["reservation"]["id"]

        response = client.post(f"/api/v1/reservations/{res_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_update_reservation_status(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        create_resp = self._make_reservation(client, vehicle_id)
        res_id = create_resp.json()["reservation"]["id"]

        response = client.patch(
            f"/api/v1/reservations/{res_id}",
            json={"status": "confirmed"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    def test_invalid_status_transition(self, client, sample_vehicle):
        vehicle_id = self._create_vehicle(client, sample_vehicle)
        create_resp = self._make_reservation(client, vehicle_id)
        res_id = create_resp.json()["reservation"]["id"]

        response = client.patch(
            f"/api/v1/reservations/{res_id}",
            json={"status": "completed"},
        )
        assert response.status_code == 400
