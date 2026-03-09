"""Test configuration and fixtures."""

import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = ":memory:"

from app.main import app
from app.database import init_db, get_connection


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Create a fresh database for each test."""
    db_path = str(tmp_path / "test.db")
    os.environ["DATABASE_PATH"] = db_path
    init_db()
    yield
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_vehicle():
    """Sample vehicle data."""
    return {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "license_plate": "ABC1D23",
        "category": "midsize",
        "fuel_type": "flex",
        "daily_rate": 159.90,
        "mileage": 15000,
        "color": "Silver",
        "seats": 5,
        "is_available": True,
    }


@pytest.fixture
def sample_vehicle_suv():
    """Sample SUV vehicle data."""
    return {
        "brand": "Jeep",
        "model": "Compass",
        "year": 2024,
        "license_plate": "XYZ9K88",
        "category": "suv",
        "fuel_type": "flex",
        "daily_rate": 249.90,
        "mileage": 5000,
        "color": "Black",
        "seats": 5,
        "is_available": True,
    }
