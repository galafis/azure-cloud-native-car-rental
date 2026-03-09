"""Vehicle models for the car rental system."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VehicleCategory(str, Enum):
    ECONOMY = "economy"
    COMPACT = "compact"
    MIDSIZE = "midsize"
    FULLSIZE = "fullsize"
    SUV = "suv"
    LUXURY = "luxury"
    VAN = "van"


class FuelType(str, Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    FLEX = "flex"


class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=100, description="Vehicle brand")
    model: str = Field(..., min_length=1, max_length=100, description="Vehicle model")
    year: int = Field(..., ge=2000, le=2030, description="Manufacturing year")
    license_plate: str = Field(..., min_length=7, max_length=8, description="License plate")
    category: VehicleCategory = Field(..., description="Vehicle category")
    fuel_type: FuelType = Field(..., description="Fuel type")
    daily_rate: float = Field(..., gt=0, description="Daily rental rate in BRL")
    mileage: int = Field(default=0, ge=0, description="Current mileage in km")
    color: str = Field(..., min_length=1, max_length=50, description="Vehicle color")
    seats: int = Field(default=5, ge=1, le=15, description="Number of seats")
    is_available: bool = Field(default=True, description="Whether the vehicle is available")


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    category: Optional[VehicleCategory] = None
    fuel_type: Optional[FuelType] = None
    daily_rate: Optional[float] = Field(None, gt=0)
    mileage: Optional[int] = Field(None, ge=0)
    color: Optional[str] = Field(None, min_length=1, max_length=50)
    seats: Optional[int] = Field(None, ge=1, le=15)
    is_available: Optional[bool] = None


class Vehicle(VehicleBase):
    id: str = Field(..., description="Unique vehicle identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
