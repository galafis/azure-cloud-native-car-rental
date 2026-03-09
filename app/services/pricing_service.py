"""Pricing engine for the car rental system."""

from datetime import date, timedelta
from typing import Optional

from app.models.pricing import PricingResponse
from app.models.vehicle import VehicleCategory


# Default pricing rules per category
DEFAULT_RATES = {
    VehicleCategory.ECONOMY: 89.90,
    VehicleCategory.COMPACT: 119.90,
    VehicleCategory.MIDSIZE: 159.90,
    VehicleCategory.FULLSIZE: 199.90,
    VehicleCategory.SUV: 249.90,
    VehicleCategory.LUXURY: 399.90,
    VehicleCategory.VAN: 299.90,
}

WEEKEND_MULTIPLIER = 1.15
WEEKLY_DISCOUNT = 0.10   # 10% discount for 7+ days
MONTHLY_DISCOUNT = 0.20  # 20% discount for 30+ days


class PricingService:
    """Service for calculating rental pricing."""

    @staticmethod
    def calculate_price(
        vehicle_id: str,
        daily_rate: float,
        start_date: date,
        end_date: date,
        category: Optional[VehicleCategory] = None,
    ) -> PricingResponse:
        """Calculate the total rental price with discounts and weekend surcharges."""
        total_days = (end_date - start_date).days
        if total_days <= 0:
            raise ValueError("end_date must be after start_date")

        weekend_days = 0
        weekday_days = 0
        current = start_date

        for _ in range(total_days):
            if current.weekday() in (5, 6):  # Saturday, Sunday
                weekend_days += 1
            else:
                weekday_days += 1
            current += timedelta(days=1)

        weekday_subtotal = weekday_days * daily_rate
        weekend_subtotal = weekend_days * daily_rate * WEEKEND_MULTIPLIER
        subtotal = weekday_subtotal + weekend_subtotal

        discount_percentage = 0.0
        if total_days >= 30:
            discount_percentage = MONTHLY_DISCOUNT
        elif total_days >= 7:
            discount_percentage = WEEKLY_DISCOUNT

        discount_amount = round(subtotal * discount_percentage, 2)
        total_amount = round(subtotal - discount_amount, 2)

        return PricingResponse(
            vehicle_id=vehicle_id,
            daily_rate=daily_rate,
            total_days=total_days,
            weekend_days=weekend_days,
            weekday_days=weekday_days,
            subtotal=round(subtotal, 2),
            discount_percentage=discount_percentage * 100,
            discount_amount=discount_amount,
            total_amount=total_amount,
            breakdown={
                "weekday_total": round(weekday_subtotal, 2),
                "weekend_total": round(weekend_subtotal, 2),
                "weekend_multiplier": WEEKEND_MULTIPLIER,
            },
        )

    @staticmethod
    def get_default_rate(category: VehicleCategory) -> float:
        """Get the default daily rate for a vehicle category."""
        return DEFAULT_RATES.get(category, 149.90)
