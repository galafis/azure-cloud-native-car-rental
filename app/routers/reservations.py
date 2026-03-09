"""Reservation API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationResponse,
    ReservationStatus,
    ReservationUpdate,
)
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/v1/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationResponse, status_code=201)
def create_reservation(reservation: ReservationCreate):
    """Create a new vehicle reservation."""
    try:
        result = ReservationService.create(reservation)
        return ReservationResponse(
            reservation=result,
            message="Reservation created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Reservation])
def list_reservations(
    status: Optional[ReservationStatus] = None,
    vehicle_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all reservations with optional filters."""
    return ReservationService.list_all(
        status=status, vehicle_id=vehicle_id, skip=skip, limit=limit
    )


@router.get("/{reservation_id}", response_model=Reservation)
def get_reservation(reservation_id: str):
    """Get a reservation by ID."""
    reservation = ReservationService.get_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.patch("/{reservation_id}", response_model=Reservation)
def update_reservation(reservation_id: str, update_data: ReservationUpdate):
    """Update reservation status or details."""
    try:
        reservation = ReservationService.update_status(reservation_id, update_data)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return reservation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/cancel", response_model=Reservation)
def cancel_reservation(reservation_id: str):
    """Cancel a reservation."""
    try:
        reservation = ReservationService.cancel(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return reservation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
