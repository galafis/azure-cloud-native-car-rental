"""Reservation models for the car rental system."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReservationBase(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    customer_name: str = Field(..., min_length=1, max_length=200, description="Customer full name")
    customer_email: str = Field(..., description="Customer email address")
    customer_document: str = Field(..., min_length=11, max_length=14, description="CPF or CNPJ")
    start_date: date = Field(..., description="Rental start date")
    end_date: date = Field(..., description="Rental end date")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    end_date: Optional[date] = None


class Reservation(ReservationBase):
    id: str = Field(..., description="Unique reservation identifier")
    status: ReservationStatus = Field(default=ReservationStatus.PENDING)
    total_amount: float = Field(..., description="Total rental amount in BRL")
    daily_rate: float = Field(..., description="Daily rate applied")
    total_days: int = Field(..., description="Total number of rental days")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ReservationResponse(BaseModel):
    reservation: Reservation
    message: str
