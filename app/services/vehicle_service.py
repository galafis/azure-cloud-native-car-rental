"""Vehicle management service."""

import uuid
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate, VehicleCategory


class VehicleService:
    """Service for vehicle CRUD operations."""

    @staticmethod
    def create(vehicle_data: VehicleCreate) -> Vehicle:
        """Create a new vehicle."""
        vehicle_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        with get_db() as conn:
            existing = conn.execute(
                "SELECT id FROM vehicles WHERE license_plate = ?",
                (vehicle_data.license_plate,),
            ).fetchone()
            if existing:
                raise ValueError(f"Vehicle with license plate {vehicle_data.license_plate} already exists")

            conn.execute(
                """INSERT INTO vehicles
                (id, brand, model, year, license_plate, category, fuel_type,
                 daily_rate, mileage, color, seats, is_available, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    vehicle_id,
                    vehicle_data.brand,
                    vehicle_data.model,
                    vehicle_data.year,
                    vehicle_data.license_plate,
                    vehicle_data.category.value,
                    vehicle_data.fuel_type.value,
                    vehicle_data.daily_rate,
                    vehicle_data.mileage,
                    vehicle_data.color,
                    vehicle_data.seats,
                    1 if vehicle_data.is_available else 0,
                    now,
                    now,
                ),
            )

        return VehicleService.get_by_id(vehicle_id)

    @staticmethod
    def get_by_id(vehicle_id: str) -> Optional[Vehicle]:
        """Get a vehicle by its ID."""
        with get_db() as conn:
            row = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
            if not row:
                return None
            return VehicleService._row_to_vehicle(row)

    @staticmethod
    def list_all(
        category: Optional[VehicleCategory] = None,
        available_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Vehicle]:
        """List vehicles with optional filtering."""
        query = "SELECT * FROM vehicles WHERE 1=1"
        params: list = []

        if category:
            query += " AND category = ?"
            params.append(category.value)
        if available_only:
            query += " AND is_available = 1"

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        with get_db() as conn:
            rows = conn.execute(query, params).fetchall()
            return [VehicleService._row_to_vehicle(row) for row in rows]

    @staticmethod
    def update(vehicle_id: str, update_data: VehicleUpdate) -> Optional[Vehicle]:
        """Update a vehicle."""
        vehicle = VehicleService.get_by_id(vehicle_id)
        if not vehicle:
            return None

        update_fields = update_data.model_dump(exclude_unset=True)
        if not update_fields:
            return vehicle

        now = datetime.utcnow().isoformat()
        update_fields["updated_at"] = now

        if "is_available" in update_fields:
            update_fields["is_available"] = 1 if update_fields["is_available"] else 0
        if "category" in update_fields and update_fields["category"]:
            update_fields["category"] = update_fields["category"].value
        if "fuel_type" in update_fields and update_fields["fuel_type"]:
            update_fields["fuel_type"] = update_fields["fuel_type"].value

        set_clause = ", ".join(f"{k} = ?" for k in update_fields)
        values = list(update_fields.values()) + [vehicle_id]

        with get_db() as conn:
            conn.execute(f"UPDATE vehicles SET {set_clause} WHERE id = ?", values)

        return VehicleService.get_by_id(vehicle_id)

    @staticmethod
    def delete(vehicle_id: str) -> bool:
        """Delete a vehicle."""
        with get_db() as conn:
            active = conn.execute(
                "SELECT id FROM reservations WHERE vehicle_id = ? AND status IN ('pending', 'confirmed', 'active')",
                (vehicle_id,),
            ).fetchone()
            if active:
                raise ValueError("Cannot delete vehicle with active reservations")

            result = conn.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
            return result.rowcount > 0

    @staticmethod
    def _row_to_vehicle(row) -> Vehicle:
        """Convert a database row to a Vehicle model."""
        return Vehicle(
            id=row["id"],
            brand=row["brand"],
            model=row["model"],
            year=row["year"],
            license_plate=row["license_plate"],
            category=row["category"],
            fuel_type=row["fuel_type"],
            daily_rate=row["daily_rate"],
            mileage=row["mileage"],
            color=row["color"],
            seats=row["seats"],
            is_available=bool(row["is_available"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
