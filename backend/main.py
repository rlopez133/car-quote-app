"""
QuoteMaster - Enhanced Insurance Quote Calculator API

This module serves as the main entry point for the QuoteMaster API.
It handles the routing and API endpoints for the insurance quote calculator.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from typing import List, Dict, Any, Optional
import json
import os
from pydantic import BaseModel

# Import from local modules
from models import (
    QuoteRequest, QuoteResponse, VehicleCategory, CoverageLevel,
    MaritalStatus, HomeOwnership, CarOwnership, VehicleValue, DrivingFrequency
)
from calculator import calculate_insurance_quote

# New models for CRM functionality
class QuoteUpdate(BaseModel):
    #id: Optional[str] = None
    customer: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date: Optional[str] = None
    vehicle: Optional[str] = None
    coverage: Optional[str] = None
    #premium: Optional[float] = None
    status: Optional[str] = None
    #zip: Optional[int] = None


class EmailRequest(BaseModel):
    quote_id: str
    subject: Optional[str] = "Your Insurance Quote"
    message: Optional[str] = None

# Path to the quotes JSON file
QUOTES_FILE = "/app/data/quotes.json"

# Create FastAPI instance
app = FastAPI(
    title="QuoteMaster API",
    description="API for calculating vehicle insurance quotes",
    version="2.0.0",
    servers=[{"url": "https://car-quote-app-backend-insurance-app.apps.ocp-beta-test.nerc.mghpcc.org", "description": "Demo dev"}]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions for CRM
def load_quotes():
    """Load quotes from JSON file."""
    if not os.path.exists(QUOTES_FILE):
        # Initialize with mock data if file doesn't exist
        mock_quotes = [
            {"id": "Q1001", "customer": "John Smith", "email": "john@example.com", "phone": "555-123-4567", "date": "2025-04-27", "vehicle": "2023 Toyota Camry (Standard)", "coverage": "Premium", "premium": "$1,250.00", "status": "new", "zip": "90210"},
            {"id": "Q1002", "customer": "Maria Garcia", "email": "maria@example.com", "phone": "555-234-5678", "date": "2025-04-27", "vehicle": "2024 Honda Civic (Economy)", "coverage": "Standard", "premium": "$980.00", "status": "new", "zip": "33178"},
            {"id": "Q1003", "customer": "Robert Johnson", "email": "robert@example.com", "phone": "555-345-6789", "date": "2025-04-26", "vehicle": "2022 Ford F-150 (Standard)", "coverage": "Premium", "premium": "$1,550.00", "status": "contacted", "zip": "60007"},
            {"id": "Q1004", "customer": "Sarah Williams", "email": "sarah@example.com", "phone": "555-456-7890", "date": "2025-04-26", "vehicle": "2024 Chevrolet Equinox (Standard)", "coverage": "Basic", "premium": "$820.00", "status": "pending", "zip": "10001"},
            {"id": "Q1005", "customer": "Michael Brown", "email": "michael@example.com", "phone": "555-567-8901", "date": "2025-04-25", "vehicle": "2023 Tesla Model 3 (Luxury)", "coverage": "Premium", "premium": "$1,680.00", "status": "new", "zip": "98101"},
            {"id": "Q1006", "customer": "Jennifer Davis", "email": "jennifer@example.com", "phone": "555-678-9012", "date": "2025-04-25", "vehicle": "2022 Nissan Altima (Standard)", "coverage": "Standard", "premium": "$1,020.00", "status": "converted", "zip": "75001"},
            {"id": "Q1007", "customer": "David Miller", "email": "david@example.com", "phone": "555-789-0123", "date": "2025-04-24", "vehicle": "2025 Hyundai Tucson (Standard)", "coverage": "Basic", "premium": "$850.00", "status": "new", "zip": "20001"},
            {"id": "Q1008", "customer": "Lisa Wilson", "email": "lisa@example.com", "phone": "555-890-1234", "date": "2025-04-24", "vehicle": "2021 BMW 3 Series (Luxury)", "coverage": "Premium", "premium": "$1,790.00", "status": "pending", "zip": "02108"},
            {"id": "Q1009", "customer": "James Taylor", "email": "james@example.com", "phone": "555-901-2345", "date": "2025-04-23", "vehicle": "2024 Kia Sorento (Standard)", "coverage": "Standard", "premium": "$1,150.00", "status": "contacted", "zip": "80202"},
            {"id": "Q1010", "customer": "Patricia Anderson", "email": "patricia@example.com", "phone": "555-012-3456", "date": "2025-04-23", "vehicle": "2022 Toyota RAV4 (Standard)", "coverage": "Basic", "premium": "$920.00", "status": "new", "zip": "30303"},
            {"id": "Q1011", "customer": "Thomas Martinez", "email": "thomas@example.com", "phone": "555-123-4567", "date": "2025-04-22", "vehicle": "2023 Lexus ES (Luxury)", "coverage": "Premium", "premium": "$1,690.00", "status": "converted", "zip": "85001"},
            {"id": "Q1012", "customer": "Elizabeth Robinson", "email": "elizabeth@example.com", "phone": "555-234-5678", "date": "2025-04-22", "vehicle": "2024 Honda Accord (Standard)", "coverage": "Standard", "premium": "$1,110.00", "status": "new", "zip": "46204"},
            {"id": "Q1013", "customer": "Charles Clark", "email": "charles@example.com", "phone": "555-345-6789", "date": "2025-04-21", "vehicle": "2022 Ford Escape (Economy)", "coverage": "Basic", "premium": "$840.00", "status": "pending", "zip": "19019"},
            {"id": "Q1014", "customer": "Susan Rodriguez", "email": "susan@example.com", "phone": "555-456-7890", "date": "2025-04-21", "vehicle": "2025 Audi A4 (Luxury)", "coverage": "Premium", "premium": "$1,850.00", "status": "new", "zip": "92101"},
            {"id": "Q1015", "customer": "Joseph Lee", "email": "joseph@example.com", "phone": "555-567-8901", "date": "2025-04-20", "vehicle": "2023 Subaru Outback (Standard)", "coverage": "Standard", "premium": "$1,050.00", "status": "contacted", "zip": "97204"}
        ]
        save_quotes(mock_quotes)
        return mock_quotes
    
    with open(QUOTES_FILE, "r") as f:
        return json.load(f)

def save_quotes(quotes):
    """Save quotes to JSON file."""
    with open(QUOTES_FILE, "w") as f:
        json.dump(quotes, f, indent=2)

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

# New CRM endpoints

@app.get("/api/quotes")
def list_quotes():
    """Return all quotes for the CRM."""
    return load_quotes()

@app.get("/api/quotes/{quote_id}")
def get_quote(quote_id: str):
    """Retrieve details for a specific quote by ID."""
    quotes = load_quotes()
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote {quote_id} not found")
    
    return quote

@app.post("/api/quotes/{quote_id}")
def post_quote(quote_id: str, update: QuoteUpdate):
    """Update details for a specific quote by ID."""
    quotes = load_quotes()
    
    quote_index = next((i for i, q in enumerate(quotes) if q["id"] == quote_id), None)
    
    if quote_index is None:
        raise HTTPException(status_code=404, detail=f"Quote {quote_id} not found")
    
    # Update the fields
    update_dict = update.dict(exclude_unset=True)
    for key, value in update_dict.items():
        quotes[quote_index][key] = value
    
    save_quotes(quotes)
    
    return {"success": True, "message": f"Quote {quote_id} updated successfully"}

@app.post("/api/quotes/{quote_id}/email")
def send_email(quote_id: str, email_request: EmailRequest):
    """Send an email for a specific quote."""
    quotes = load_quotes()
    
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote {quote_id} not found")
    
    # In a real implementation, you would send an actual email here
    # For the demo, just update the status
    quote_index = next((i for i, q in enumerate(quotes) if q["id"] == quote_id))
    quotes[quote_index]["status"] = "contacted"
    
    save_quotes(quotes)
    
    return {
        "success": True, 
        "message": f"Email sent for quote {quote_id} to {quote['email']}"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
