"""Availability and pricing API routes."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.vehicle import Vehicle, VehicleCategory
from app.models.pricing import PricingResponse
from app.services.availability_service import AvailabilityService
from app.services.pricing_service import PricingService
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/api/v1", tags=["Availability & Pricing"])


@router.get("/availability", response_model=List[Vehicle])
def check_availability(
    start_date: date = Query(..., description="Rental start date"),
    end_date: date = Query(..., description="Rental end date"),
    category: Optional[VehicleCategory] = None,
):
    """Find available vehicles for a date range."""
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    return AvailabilityService.find_available_vehicles(start_date, end_date, category)


@router.get("/availability/{vehicle_id}")
def check_vehicle_availability(
    vehicle_id: str,
    start_date: date = Query(..., description="Rental start date"),
    end_date: date = Query(..., description="Rental end date"),
):
    """Check if a specific vehicle is available."""
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    vehicle = VehicleService.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    is_available = AvailabilityService.check_vehicle_available(
        vehicle_id, start_date, end_date
    )
    return {"vehicle_id": vehicle_id, "available": is_available}


@router.get("/pricing/{vehicle_id}", response_model=PricingResponse)
def calculate_pricing(
    vehicle_id: str,
    start_date: date = Query(..., description="Rental start date"),
    end_date: date = Query(..., description="Rental end date"),
):
    """Calculate rental pricing for a vehicle and date range."""
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    vehicle = VehicleService.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return PricingService.calculate_price(
        vehicle_id=vehicle.id,
        daily_rate=vehicle.daily_rate,
        start_date=start_date,
        end_date=end_date,
        category=vehicle.category,
    )


@router.get("/vehicles/{vehicle_id}/schedule")
def get_vehicle_schedule(vehicle_id: str):
    """Get the reservation schedule for a vehicle."""
    vehicle = VehicleService.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return AvailabilityService.get_vehicle_schedule(vehicle_id)
