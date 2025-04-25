"""
QuoteMaster - Enhanced Insurance Quote Calculator API

This module serves as the main entry point for the QuoteMaster API.
It handles the routing and API endpoints for the insurance quote calculator.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from typing import List, Dict, Any

# Import from local modules
from models import (
    QuoteRequest, QuoteResponse, VehicleCategory, CoverageLevel,
    MaritalStatus, HomeOwnership, CarOwnership, VehicleValue, DrivingFrequency
)
from calculator import calculate_insurance_quote

# Create FastAPI instance
app = FastAPI(
    title="QuoteMaster API",
    description="API for calculating vehicle insurance quotes",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "QuoteMaster API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/vehicle-years", response_model=List[int])
def get_available_years():
    """
    Return a list of available vehicle years.
    
    Returns a list of years from current year going back 20 years.
    """
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 21, -1))
    return years

@app.get("/vehicle-categories", response_model=List[str])
def get_vehicle_categories():
    """Get a list of valid vehicle categories."""
    return [category.value for category in VehicleCategory]

@app.get("/coverage-levels", response_model=List[str])
def get_coverage_levels():
    """Get a list of valid coverage levels."""
    return [level.value for level in CoverageLevel]

@app.get("/marital-statuses", response_model=List[str])
def get_marital_statuses():
    """Get a list of valid marital statuses."""
    return [status.value for status in MaritalStatus]

@app.get("/home-ownership-options", response_model=List[str])
def get_home_ownership_options():
    """Get a list of valid home ownership options."""
    return [option.value for option in HomeOwnership]

@app.get("/car-ownership-options", response_model=List[str])
def get_car_ownership_options():
    """Get a list of valid car ownership options."""
    return [option.value for option in CarOwnership]

@app.get("/vehicle-value-ranges", response_model=List[str])
def get_vehicle_value_ranges():
    """Get a list of valid vehicle value ranges."""
    return [value_range.value for value_range in VehicleValue]

@app.get("/driving-frequency-options", response_model=List[str])
def get_driving_frequency_options():
    """Get a list of valid driving frequency options."""
    return [option.value for option in DrivingFrequency]

@app.post("/calculate-quote")
def calculate_quote(request: QuoteRequest):
    """
    Calculate an insurance quote based on vehicle and driver details.
    
    Args:
        request: The quote request parameters
        
    Returns:
        A QuoteResponse with quote details and price
    """
    try:
        # Calculate quote using business logic from calculator module
        quote_result = calculate_insurance_quote(
            vehicle_category=request.vehicle_category.value,
            vehicle_year=request.vehicle_year,
            coverage_level=request.coverage_level.value,
            marital_status=request.marital_status.value,
            age=request.age,
            home_ownership=request.home_ownership.value,
            car_ownership=request.car_ownership.value,
            vehicle_value=request.vehicle_value.value,
            driving_frequency=request.driving_frequency.value,
            zip_code=request.zip_code
        )
        
        # Return formatted response
        return QuoteResponse(
            # Customer information
            vehicle_category=request.vehicle_category.value,
            vehicle_year=request.vehicle_year,
            marital_status=request.marital_status.value,
            age=request.age,
            home_ownership=request.home_ownership.value,
            car_ownership=request.car_ownership.value,
            vehicle_value=request.vehicle_value.value,
            driving_frequency=request.driving_frequency.value,
            zip_code=request.zip_code,
            
            # Coverage selection
            coverage_level=request.coverage_level.value,
            
            # Coverage details, factors, and totals from the calculator
            coverages=quote_result["coverages"],
            base_premium=quote_result["base_premium"],
            age_factor=quote_result["age_factor"],
            location_factor=quote_result["location_factor"],
            marital_factor=quote_result["marital_factor"],
            vehicle_factor=quote_result["vehicle_factor"],
            driving_factor=quote_result["driving_factor"],
            discounts=quote_result["discounts"],
            subtotal=quote_result["subtotal"],
            total_discounts=quote_result["total_discounts"],
            final_premium=quote_result["final_premium"],
            
            # Reference information
            quote_id=quote_result["quote_id"],
            expiration_date=quote_result["expiration_date"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
