"""Pricing models for the car rental system."""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.vehicle import VehicleCategory


class PricingRule(BaseModel):
    category: VehicleCategory
    base_daily_rate: float = Field(..., gt=0)
    weekend_multiplier: float = Field(default=1.2, gt=0)
    weekly_discount: float = Field(default=0.1, ge=0, le=1, description="Discount for 7+ days")
    monthly_discount: float = Field(default=0.2, ge=0, le=1, description="Discount for 30+ days")


class PricingResponse(BaseModel):
    vehicle_id: str
    daily_rate: float
    total_days: int
    weekend_days: int
    weekday_days: int
    subtotal: float
    discount_percentage: float
    discount_amount: float
    total_amount: float
    breakdown: Optional[dict] = None
