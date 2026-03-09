"""Vehicle API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate, VehicleCategory
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/api/v1/vehicles", tags=["Vehicles"])


@router.post("/", response_model=Vehicle, status_code=201)
def create_vehicle(vehicle: VehicleCreate):
    """Create a new vehicle in the fleet."""
    try:
        return VehicleService.create(vehicle)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=List[Vehicle])
def list_vehicles(
    category: Optional[VehicleCategory] = None,
    available_only: bool = Query(False, description="Filter only available vehicles"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all vehicles with optional filters."""
    return VehicleService.list_all(
        category=category, available_only=available_only, skip=skip, limit=limit
    )


@router.get("/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str):
    """Get a vehicle by ID."""
    vehicle = VehicleService.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.patch("/{vehicle_id}", response_model=Vehicle)
def update_vehicle(vehicle_id: str, update_data: VehicleUpdate):
    """Update vehicle information."""
    vehicle = VehicleService.update(vehicle_id, update_data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: str):
    """Remove a vehicle from the fleet."""
    try:
        deleted = VehicleService.delete(vehicle_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Vehicle not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
