"""Availability checking service for the car rental system."""

from datetime import date
from typing import List

from app.database import get_db
from app.models.vehicle import Vehicle, VehicleCategory
from app.services.vehicle_service import VehicleService


class AvailabilityService:
    """Service for checking vehicle availability."""

    @staticmethod
    def check_vehicle_available(vehicle_id: str, start_date: date, end_date: date) -> bool:
        """Check if a specific vehicle is available for the given date range."""
        with get_db() as conn:
            vehicle = conn.execute(
                "SELECT is_available FROM vehicles WHERE id = ?", (vehicle_id,)
            ).fetchone()
            if not vehicle or not vehicle["is_available"]:
                return False

            conflict = conn.execute(
                """SELECT id FROM reservations
                WHERE vehicle_id = ?
                AND status IN ('pending', 'confirmed', 'active')
                AND start_date < ?
                AND end_date > ?""",
                (vehicle_id, end_date.isoformat(), start_date.isoformat()),
            ).fetchone()

            return conflict is None

    @staticmethod
    def find_available_vehicles(
        start_date: date,
        end_date: date,
        category: VehicleCategory = None,
    ) -> List[Vehicle]:
        """Find all available vehicles for a given date range."""
        query = """
            SELECT v.* FROM vehicles v
            WHERE v.is_available = 1
            AND v.id NOT IN (
                SELECT r.vehicle_id FROM reservations r
                WHERE r.status IN ('pending', 'confirmed', 'active')
                AND r.start_date < ?
                AND r.end_date > ?
            )
        """
        params: list = [end_date.isoformat(), start_date.isoformat()]

        if category:
            query += " AND v.category = ?"
            params.append(category.value)

        query += " ORDER BY v.daily_rate ASC"

        with get_db() as conn:
            rows = conn.execute(query, params).fetchall()
            return [VehicleService._row_to_vehicle(row) for row in rows]

    @staticmethod
    def get_vehicle_schedule(vehicle_id: str) -> list:
        """Get all reservations for a vehicle (for calendar view)."""
        with get_db() as conn:
            rows = conn.execute(
                """SELECT id, customer_name, start_date, end_date, status
                FROM reservations
                WHERE vehicle_id = ?
                AND status IN ('pending', 'confirmed', 'active')
                ORDER BY start_date ASC""",
                (vehicle_id,),
            ).fetchall()
            return [dict(row) for row in rows]
