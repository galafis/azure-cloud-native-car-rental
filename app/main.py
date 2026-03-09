"""FastAPI application for the Cloud-Native Car Rental system."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import vehicles, reservations, availability

app = FastAPI(
    title="Car Rental API",
    description="Cloud-Native Car Rental Management System - Vehicle fleet management, "
    "reservations, pricing engine, and availability checking.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router)
app.include_router(reservations.router)
app.include_router(availability.router)


@app.on_event("startup")
def startup():
    """Initialize database on application startup."""
    init_db()


@app.get("/", tags=["Health"])
def root():
    """API root endpoint."""
    return {
        "service": "Car Rental API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
