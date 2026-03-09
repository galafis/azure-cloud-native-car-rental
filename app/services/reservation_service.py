"""Reservation management service."""

import uuid
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
    ReservationUpdate,
)
from app.services.availability_service import AvailabilityService
from app.services.pricing_service import PricingService
from app.services.vehicle_service import VehicleService


class ReservationService:
    """Service for reservation management operations."""

    @staticmethod
    def create(reservation_data: ReservationCreate) -> Reservation:
        """Create a new reservation."""
        vehicle = VehicleService.get_by_id(reservation_data.vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {reservation_data.vehicle_id} not found")

        if not AvailabilityService.check_vehicle_available(
            reservation_data.vehicle_id,
            reservation_data.start_date,
            reservation_data.end_date,
        ):
            raise ValueError(
                f"Vehicle {reservation_data.vehicle_id} is not available for the selected dates"
            )

        pricing = PricingService.calculate_price(
            vehicle_id=vehicle.id,
            daily_rate=vehicle.daily_rate,
            start_date=reservation_data.start_date,
            end_date=reservation_data.end_date,
            category=vehicle.category,
        )

        reservation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        with get_db() as conn:
            conn.execute(
                """INSERT INTO reservations
                (id, vehicle_id, customer_name, customer_email, customer_document,
                 start_date, end_date, status, total_amount, daily_rate, total_days,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    reservation_id,
                    reservation_data.vehicle_id,
                    reservation_data.customer_name,
                    reservation_data.customer_email,
                    reservation_data.customer_document,
                    reservation_data.start_date.isoformat(),
                    reservation_data.end_date.isoformat(),
                    ReservationStatus.PENDING.value,
                    pricing.total_amount,
                    vehicle.daily_rate,
                    pricing.total_days,
                    now,
                    now,
                ),
            )

        return ReservationService.get_by_id(reservation_id)

    @staticmethod
    def get_by_id(reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by its ID."""
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if not row:
                return None
            return ReservationService._row_to_reservation(row)

    @staticmethod
    def list_all(
        status: Optional[ReservationStatus] = None,
        vehicle_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Reservation]:
        """List reservations with optional filtering."""
        query = "SELECT * FROM reservations WHERE 1=1"
        params: list = []

        if status:
            query += " AND status = ?"
            params.append(status.value)
        if vehicle_id:
            query += " AND vehicle_id = ?"
            params.append(vehicle_id)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        with get_db() as conn:
            rows = conn.execute(query, params).fetchall()
            return [ReservationService._row_to_reservation(row) for row in rows]

    @staticmethod
    def update_status(reservation_id: str, update_data: ReservationUpdate) -> Optional[Reservation]:
        """Update a reservation's status."""
        reservation = ReservationService.get_by_id(reservation_id)
        if not reservation:
            return None

        valid_transitions = {
            ReservationStatus.PENDING: [ReservationStatus.CONFIRMED, ReservationStatus.CANCELLED],
            ReservationStatus.CONFIRMED: [ReservationStatus.ACTIVE, ReservationStatus.CANCELLED],
            ReservationStatus.ACTIVE: [ReservationStatus.COMPLETED, ReservationStatus.CANCELLED],
            ReservationStatus.COMPLETED: [],
            ReservationStatus.CANCELLED: [],
        }

        if update_data.status:
            allowed = valid_transitions.get(reservation.status, [])
            if update_data.status not in allowed:
                raise ValueError(
                    f"Cannot transition from {reservation.status.value} to {update_data.status.value}"
                )

        now = datetime.utcnow().isoformat()
        updates = {"updated_at": now}

        if update_data.status:
            updates["status"] = update_data.status.value
        if update_data.end_date:
            updates["end_date"] = update_data.end_date.isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [reservation_id]

        with get_db() as conn:
            conn.execute(f"UPDATE reservations SET {set_clause} WHERE id = ?", values)

        return ReservationService.get_by_id(reservation_id)

    @staticmethod
    def cancel(reservation_id: str) -> Optional[Reservation]:
        """Cancel a reservation."""
        return ReservationService.update_status(
            reservation_id, ReservationUpdate(status=ReservationStatus.CANCELLED)
        )

    @staticmethod
    def _row_to_reservation(row) -> Reservation:
        """Convert a database row to a Reservation model."""
        return Reservation(
            id=row["id"],
            vehicle_id=row["vehicle_id"],
            customer_name=row["customer_name"],
            customer_email=row["customer_email"],
            customer_document=row["customer_document"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            status=row["status"],
            total_amount=row["total_amount"],
            daily_rate=row["daily_rate"],
            total_days=row["total_days"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
