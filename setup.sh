#!/bin/bash
# Enhanced QuoteMaster setup script

# Print colorful messages
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Enhanced QuoteMaster - Setup Script  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Check for Docker and Docker Compose / Podman
echo -e "${YELLOW}Checking prerequisites...${NC}"

if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo -e "${GREEN}✓ Podman is installed.${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Docker is installed.${NC}"
else
    echo -e "${RED}Neither Podman nor Docker is installed. Please install either one first.${NC}"
    echo "Visit https://docs.docker.com/get-docker/ or https://podman.io/getting-started/installation"
    exit 1
fi

echo

# Create directory structure
echo -e "${YELLOW}Creating project structure...${NC}"

# Create directories
mkdir -p backend
mkdir -p frontend/css
mkdir -p frontend/js

echo -e "${GREEN}✓ Directory structure created.${NC}"
echo

# Create backend files
echo -e "${YELLOW}Creating enhanced backend files...${NC}"

# models.py
cat > backend/models.py << 'EOF'
"""
Data models for the QuoteMaster API.

This module defines the Pydantic models used for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
import re

# Using Enum instead of Literal for better compatibility
class VehicleCategory(str, Enum):
    ECONOMY = "Economy"
    STANDARD = "Standard"
    LUXURY = "Luxury"

class CoverageLevel(str, Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"

class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class HomeOwnership(str, Enum):
    OWN = "Own"
    RENT = "Rent"
    OTHER = "Other"

class CarOwnership(str, Enum):
    OWN = "Own"
    LEASE = "Lease"
    FINANCE = "Finance"

class VehicleValue(str, Enum):
    LOW = "Under $5,000"
    MEDIUM = "$5,000 - $40,000"
    HIGH = "Over $40,000"

class DrivingFrequency(str, Enum):
    LOW = "Very Little"
    MEDIUM = "Average"
    HIGH = "A Lot"

class QuoteRequest(BaseModel):
    """
    Model for insurance quote request data.
    """
    vehicle_category: VehicleCategory = Field(
        ..., 
        description="The category of the vehicle"
    )
    vehicle_year: int = Field(
        ..., 
        description="The manufacturing year of the vehicle"
    )
    coverage_level: CoverageLevel = Field(
        ..., 
        description="The level of insurance coverage"
    )
    marital_status: MaritalStatus = Field(
        ...,
        description="Marital status of the primary driver"
    )
    age: int = Field(
        ...,
        description="Age of the primary driver",
        ge=16,  # Must be at least 16 years old to drive
        le=120  # Reasonable upper limit
    )
    home_ownership: HomeOwnership = Field(
        ...,
        description="Home ownership status"
    )
    car_ownership: CarOwnership = Field(
        ...,
        description="Car ownership status"
    )
    vehicle_value: VehicleValue = Field(
        ...,
        description="Estimated value of the vehicle"
    )
    driving_frequency: DrivingFrequency = Field(
        ...,
        description="How often the vehicle is driven"
    )
    zip_code: str = Field(
        ...,
        description="Residential ZIP code of primary driver"
    )
    
    @validator('vehicle_year')
    def validate_year(cls, v):
        """Validate that vehicle year is within acceptable range."""
        current_year = datetime.now().year
        min_year = current_year - 20
        
        if v < min_year or v > current_year + 1:  # Allow next year's models
            raise ValueError(f"Vehicle year must be between {min_year} and {current_year + 1}")
        return v
        
    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate zip code format."""
        # Check that it's a 5-digit US ZIP code
        if not re.match(r'^\d{5}$', v):
            raise ValueError("ZIP code must be a 5-digit number")
        return v

class CoverageDetail(BaseModel):
    """Model for individual coverage details."""
    name: str = Field(..., description="Name of the coverage")
    amount: str = Field(..., description="Coverage amount/limit")
    premium: float = Field(..., description="Premium for this coverage")
    description: str = Field(..., description="Description of what this coverage protects")

class Discount(BaseModel):
    """Model for insurance discount details."""
    name: str = Field(..., description="Name of the discount")
    amount: float = Field(..., description="Discount amount in dollars")
    description: str = Field(..., description="Description of the discount conditions")

class QuoteResponse(BaseModel):
    """
    Model for insurance quote response data.
    """
    # Customer information
    vehicle_category: str = Field(..., description="The category of the vehicle")
    vehicle_year: int = Field(..., description="The manufacturing year of the vehicle")
    marital_status: str = Field(..., description="Marital status of the primary driver")
    age: int = Field(..., description="Age of the primary driver")
    home_ownership: str = Field(..., description="Home ownership status")
    car_ownership: str = Field(..., description="Car ownership status")
    vehicle_value: str = Field(..., description="Estimated value of the vehicle")
    driving_frequency: str = Field(..., description="How often the vehicle is driven")
    zip_code: str = Field(..., description="Residential ZIP code")
    
    # Coverage selection
    coverage_level: str = Field(..., description="The level of insurance coverage")
    
    # Coverage details
    coverages: list[CoverageDetail] = Field(..., description="List of coverage details")
    
    # Pricing information
    base_premium: float = Field(..., description="Base premium before adjustments")
    age_factor: float = Field(..., description="Age adjustment factor")
    location_factor: float = Field(..., description="Location-based adjustment factor")
    marital_factor: float = Field(..., description="Marital status adjustment factor")
    vehicle_factor: float = Field(..., description="Vehicle-based adjustment factor")
    driving_factor: float = Field(..., description="Driving frequency adjustment factor")
    
    # Discounts
    discounts: list[Discount] = Field(..., description="List of applicable discounts")
    
    # Totals
    subtotal: float = Field(..., description="Subtotal before discounts")
    total_discounts: float = Field(..., description="Total discount amount")
    final_premium: float = Field(..., description="Final premium after all adjustments and discounts")
    
    # Reference/ID information
    quote_id: str = Field(..., description="Unique quote identifier")
    expiration_date: str = Field(..., description="Date when this quote expires")
EOF

# calculator.py
cat > backend/calculator.py << 'EOF'
"""
Enhanced insurance quote calculator business logic.

This module provides the core calculation logic for determining insurance quotes
based on vehicle details, driver information, and coverage options.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import hashlib
import random

def calculate_insurance_quote(
    vehicle_category: str,
    vehicle_year: int,
    coverage_level: str,
    marital_status: str,
    age: int,
    home_ownership: str,
    car_ownership: str,
    vehicle_value: str,
    driving_frequency: str,
    zip_code: str
) -> Dict[str, Any]:
    """
    Calculate an insurance quote based on input parameters.
    
    Args:
        vehicle_category: Category of the vehicle (Economy, Standard, Luxury)
        vehicle_year: Manufacturing year of the vehicle
        coverage_level: Level of insurance coverage (Basic, Standard, Premium)
        marital_status: Marital status of primary driver
        age: Age of primary driver
        home_ownership: Home ownership status
        car_ownership: Car ownership status
        vehicle_value: Value range of the vehicle
        driving_frequency: How often the vehicle is driven
        zip_code: Residential ZIP code of primary driver
        
    Returns:
        Dictionary containing calculated price and adjustment factors
    """
    # Basic premium calculations based on coverage level
    coverages = _calculate_coverage_details(coverage_level, vehicle_value)
    
    # Calculate various factor adjustments
    base_premium = sum(coverage['premium'] for coverage in coverages)
    
    # Calculate adjustment factors
    age_factor = _calculate_age_factor(age)
    location_factor = _calculate_location_factor(zip_code)
    marital_factor = _calculate_marital_factor(marital_status)
    vehicle_factor = _calculate_vehicle_factor(vehicle_category, vehicle_year, vehicle_value, car_ownership)
    driving_factor = _calculate_driving_factor(driving_frequency)
    
    # Apply factors to calculate adjusted premium
    adjusted_premium = base_premium * age_factor * location_factor * marital_factor * vehicle_factor * driving_factor
    
    # Calculate applicable discounts
    discounts = _calculate_discounts(
        marital_status=marital_status, 
        age=age, 
        home_ownership=home_ownership, 
        car_ownership=car_ownership,
        vehicle_year=vehicle_year,
        coverage_level=coverage_level
    )
    
    total_discounts = sum(discount['amount'] for discount in discounts)
    
    # Calculate final premium
    final_premium = max(50, adjusted_premium - total_discounts)  # Minimum premium of $50
    
    # Generate a quote ID and expiration date
    quote_id = f"QM-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    expiration_date = (datetime.now().replace(hour=23, minute=59, second=59) + 
                      timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Return all calculation details
    return {
        "coverages": coverages,
        "base_premium": round(base_premium, 2),
        "age_factor": round(age_factor, 2),
        "location_factor": round(location_factor, 2),
        "marital_factor": round(marital_factor, 2),
        "vehicle_factor": round(vehicle_factor, 2),
        "driving_factor": round(driving_factor, 2),
        "discounts": discounts,
        "subtotal": round(adjusted_premium, 2),
        "total_discounts": round(total_discounts, 2),
        "final_premium": round(final_premium, 2),
        "quote_id": quote_id,
        "expiration_date": expiration_date
    }

def _calculate_coverage_details(coverage_level: str, vehicle_value: str) -> List[Dict[str, Any]]:
    """Calculate the individual coverage details based on coverage level."""
    # Determine base multiplier from coverage level
    multiplier = {
        "Basic": 1.0,
        "Standard": 1.3,
        "Premium": 1.7
    }.get(coverage_level, 1.0)
    
    # Determine value multiplier from vehicle value
    value_multiplier = {
        "Under $5,000": 0.8,
        "$5,000 - $40,000": 1.0,
        "Over $40,000": 1.4
    }.get(vehicle_value, 1.0)
    
    # Define coverage types and base premiums
    coverages = [
        {
            "name": "Bodily Injury Liability",
            "amount": _get_bodily_injury_limit(coverage_level),
            "premium": 250 * multiplier,
            "description": "Covers costs due to injuries you cause to others in an accident"
        },
        {
            "name": "Property Damage Liability",
            "amount": _get_property_damage_limit(coverage_level),
            "premium": 150 * multiplier,
            "description": "Covers costs due to damage you cause to others' property"
        },
        {
            "name": "Uninsured/Underinsured Motorist Bodily Injury",
            "amount": _get_um_limit(coverage_level),
            "premium": 100 * multiplier,
            "description": "Covers your injuries caused by an uninsured or underinsured driver"
        }
    ]
    
    # Add optional coverages based on level
    if coverage_level in ["Standard", "Premium"]:
        coverages.append({
            "name": "Rental Car Coverage",
            "amount": "$30/day, $900 maximum" if coverage_level == "Premium" else "$25/day, $750 maximum",
            "premium": 50 * (1.2 if coverage_level == "Premium" else 1.0),
            "description": "Covers rental car costs while your car is being repaired"
        })
    
    # Add comprehensive and collision for Standard and Premium
    if coverage_level in ["Standard", "Premium"]:
        # Deductible is lower for Premium
        deductible = "$250" if coverage_level == "Premium" else "$500"
        coverages.append({
            "name": "Comprehensive",
            "amount": f"{deductible} deductible",
            "premium": 200 * value_multiplier * (1.2 if coverage_level == "Premium" else 1.0),
            "description": "Covers damage to your car from non-accident causes like theft, vandalism, etc."
        })
        coverages.append({
            "name": "Collision",
            "amount": f"{deductible} deductible",
            "premium": 300 * value_multiplier * (1.2 if coverage_level == "Premium" else 1.0),
            "description": "Covers damage to your car from accidents regardless of fault"
        })
    
    # Round all premiums to 2 decimal places
    for coverage in coverages:
        coverage['premium'] = round(coverage['premium'], 2)
    
    return coverages

def _get_bodily_injury_limit(coverage_level: str) -> str:
    """Get the bodily injury liability limit based on coverage level."""
    limits = {
        "Basic": "$15,000/$30,000",
        "Standard": "$50,000/$100,000",
        "Premium": "$100,000/$300,000"
    }
    return limits.get(coverage_level, "$15,000/$30,000")

def _get_property_damage_limit(coverage_level: str) -> str:
    """Get the property damage liability limit based on coverage level."""
    limits = {
        "Basic": "$5,000",
        "Standard": "$25,000",
        "Premium": "$50,000"
    }
    return limits.get(coverage_level, "$5,000")

def _get_um_limit(coverage_level: str) -> str:
    """Get the uninsured motorist coverage limit based on coverage level."""
    limits = {
        "Basic": "$15,000/$30,000",
        "Standard": "$50,000/$100,000",
        "Premium": "$100,000/$300,000"
    }
    return limits.get(coverage_level, "$15,000/$30,000")

def _calculate_age_factor(age: int) -> float:
    """Calculate premium adjustment factor based on driver's age."""
    if age < 20:
        return 2.0  # Highest risk category
    elif age < 25:
        return 1.5  # High risk
    elif age < 30:
        return 1.2  # Moderate risk
    elif age < 60:
        return 1.0  # Base rate
    elif age < 70:
        return 1.1  # Slightly increased risk
    else:
        return 1.3  # Higher risk for elderly drivers

def _calculate_location_factor(zip_code: str) -> float:
    """Calculate premium adjustment factor based on location (ZIP code)."""
    # Using a deterministic but random-looking approach based on ZIP
    # In a real app, this would use actuarial tables based on location risk
    zip_hash = int(hashlib.md5(zip_code.encode()).hexdigest(), 16) % 100
    
    # Normalize to a factor between 0.8 and 1.5
    return 0.8 + (zip_hash / 100) * 0.7

def _calculate_marital_factor(marital_status: str) -> float:
    """Calculate premium adjustment factor based on marital status."""
    factors = {
        "Single": 1.1,  # Slightly higher risk
        "Married": 0.9,  # Lower risk
        "Divorced": 1.0,  # Base
        "Widowed": 0.95  # Slightly lower risk
    }
    return factors.get(marital_status, 1.0)

def _calculate_vehicle_factor(
    vehicle_category: str,
    vehicle_year: int,
    vehicle_value: str,
    car_ownership: str
) -> float:
    """Calculate premium adjustment factor based on vehicle details."""
    # Base factor by category
    category_factors = {
        "Economy": 0.9,
        "Standard": 1.0,
        "Luxury": 1.3
    }
    category_factor = category_factors.get(vehicle_category, 1.0)
    
    # Age factor based on vehicle year
    current_year = datetime.now().year
    vehicle_age = current_year - vehicle_year
    age_factor = max(0.8, 1.2 - (vehicle_age * 0.03))  # Newer cars cost more
    
    # Value factor
    value_factors = {
        "Under $5,000": 0.8,
        "$5,000 - $40,000": 1.0,
        "Over $40,000": 1.3
    }
    value_factor = value_factors.get(vehicle_value, 1.0)
    
    # Ownership factor
    ownership_factors = {
        "Own": 0.95,  # Slight discount for ownership
        "Finance": 1.0,  # Base rate
        "Lease": 1.05   # Slight increase for leasing
    }
    ownership_factor = ownership_factors.get(car_ownership, 1.0)
    
    # Combine factors
    return category_factor * age_factor * value_factor * ownership_factor

def _calculate_driving_factor(driving_frequency: str) -> float:
    """Calculate premium adjustment factor based on driving frequency."""
    factors = {
        "Very Little": 0.8,  # Lower risk due to less exposure
        "Average": 1.0,      # Base rate
        "A Lot": 1.2         # Higher risk due to more exposure
    }
    return factors.get(driving_frequency, 1.0)

def _calculate_discounts(
    marital_status: str,
    age: int,
    home_ownership: str,
    car_ownership: str,
    vehicle_year: int,
    coverage_level: str
) -> List[Dict[str, Any]]:
    """Calculate applicable discounts based on customer profile."""
    discounts = []
    current_year = datetime.now().year
    
    # Homeowner discount
    if home_ownership == "Own":
        discounts.append({
            "name": "Homeowner Discount",
            "amount": 75.0,
            "description": "Discount for customers who own their home"
        })
    
    # Marriage discount
    if marital_status == "Married":
        discounts.append({
            "name": "Married Driver Discount",
            "amount": 50.0,
            "description": "Discount for married drivers"
        })
    
    # Mature driver discount
    if age >= 30 and age <= 65:
        discounts.append({
            "name": "Experienced Driver Discount",
            "amount": 40.0,
            "description": "Discount for drivers aged 30-65"
        })
    
    # Multi-policy potential discount
    if home_ownership == "Own" and coverage_level == "Premium":
        discounts.append({
            "name": "Multi-Policy Discount",
            "amount": 100.0,
            "description": "Discount for bundling auto with homeowners insurance"
        })
    
    # Safe vehicle discount for newer cars
    if current_year - vehicle_year <= 3:
        discounts.append({
            "name": "New Vehicle Discount",
            "amount": 60.0,
            "description": "Discount for newer vehicles with modern safety features"
        })
    
    # Loyalty discount for vehicle owners
    if car_ownership == "Own":
        discounts.append({
            "name": "Vehicle Owner Discount",
            "amount": 30.0,
            "description": "Discount for customers who own their vehicles"
        })
    
    # Round all discount amounts to 2 decimal places
    for discount in discounts:
        discount['amount'] = round(discount['amount'], 2)
    
    return discounts
EOF

# main.py
cat > backend/main.py << 'EOF'
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
EOF

# requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.95.1
uvicorn==0.22.0
pydantic==1.10.7
EOF

# Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo -e "${GREEN}✓ Backend files created.${NC}"
echo

# Create frontend files
echo -e "${YELLOW}Creating enhanced frontend files...${NC}"

# index.html
cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuoteMaster - Car Insurance Quote Calculator</title>
    <link rel="stylesheet" href="css/normalize.css">
    <link rel="stylesheet" href="css/styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1>QuoteMaster</h1>
            <p class="tagline">Fast, accurate car insurance quotes</p>
        </div>
    </header>

    <main class="container">
        <section class="quote-calculator">
            <div class="card">
                <h2>Get Your Quote</h2>
                <p>Fill out the form below to receive an instant quote for your vehicle.</p>
                
                <form id="quote-form" class="quote-form">
                    <!-- Vehicle Information -->
                    <div class="form-section">
                        <h3>Vehicle Information</h3>
                        
                        <div class="form-group">
                            <label for="vehicle-category">Vehicle Category</label>
                            <select id="vehicle-category" name="vehicle-category" required>
                                <option value="" disabled selected>-- Select Category --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                            <p class="help-text">Economy: compact & subcompact cars. Standard: mid-size & family cars. Luxury: high-end & premium vehicles.</p>
                        </div>
                        
                        <div class="form-group">
                            <label for="vehicle-year">Vehicle Year</label>
                            <select id="vehicle-year" name="vehicle-year" required>
                                <option value="" disabled selected>-- Select Year --</option>
                                <!-- Will be populated by JavaScript -->
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="vehicle-value">Vehicle Value</label>
                            <select id="vehicle-value" name="vehicle-value" required>
                                <option value="" disabled selected>-- Select Value Range --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="car-ownership">Car Ownership</label>
                            <select id="car-ownership" name="car-ownership" required>
                                <option value="" disabled selected>-- Select Ownership --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                    </div>
                    
                    <!-- Driver Information -->
                    <div class="form-section">
                        <h3>Driver Information</h3>
                        
                        <div class="form-group">
                            <label for="driver-age">Age of Primary Driver</label>
                            <input type="number" id="driver-age" name="driver-age" min="16" max="120" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="marital-status">Marital Status</label>
                            <select id="marital-status" name="marital-status" required>
                                <option value="" disabled selected>-- Select Status --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="home-ownership">Home Ownership</label>
                            <select id="home-ownership" name="home-ownership" required>
                                <option value="" disabled selected>-- Select Ownership --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="driving-frequency">Time Spent Driving</label>
                            <select id="driving-frequency" name="driving-frequency" required>
                                <option value="" disabled selected>-- Select Frequency --</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="zip-code">ZIP Code</label>
                            <input type="text" id="zip-code" name="zip-code" pattern="[0-9]{5}" maxlength="5" required>
                            <p class="help-text">Enter your 5-digit ZIP code</p>
                        </div>
                    </div>
                    
                    <!-- Coverage Information -->
                    <div class="form-section">
                        <h3>Coverage Level</h3>
                        <div class="radio-group">
                            <div class="radio-option">
                                <input type="radio" id="basic" name="coverage-level" value="Basic" required>
                                <label for="basic">Basic</label>
                                <p class="help-text">Minimal coverage meeting state requirements. Higher out-of-pocket costs if you have an accident.</p>
                            </div>
                            <div class="radio-option">
                                <input type="radio" id="standard" name="coverage-level" value="Standard">
                                <label for="standard">Standard</label>
                                <p class="help-text">Balanced coverage with moderate out-of-pocket costs. Includes comprehensive and collision.</p>
                            </div>
                            <div class="radio-option">
                                <input type="radio" id="premium" name="coverage-level" value="Premium">
                                <label for="premium">Premium</label>
                                <p class="help-text">Maximum protection with lowest out-of-pocket costs. Includes all available coverages.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Calculate Quote</button>
                    </div>
                </form>

                <div id="quote-result" class="quote-result hidden">
                    <!-- Will be populated by JavaScript -->
                </div>

                <div id="loading-spinner" class="loading-spinner hidden">
                    <div class="spinner"></div>
                    <p>Calculating your quote...</p>
                </div>
            </div>
        </section>

        <section class="features">
            <h2>Why Choose QuoteMaster?</h2>
            
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-icon">⚡</div>
                    <h3>Fast Quotes</h3>
                    <p>Get your quote in seconds, not minutes.</p>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">💰</div>
                    <h3>Save Money</h3>
                    <p>Compare options to find the best value.</p>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">🔒</div>
                    <h3>Secure</h3>
                    <p>Your information is always protected.</p>
                </div>
                
                <div class="feature-item">
                    <div class="feature-icon">📊</div>
                    <h3>Transparent</h3>
                    <p>See exactly how your quote is calculated.</p>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 QuoteMaster. All rights reserved.</p>
            <p class="disclaimer">This is a demo application. Quotes are for illustration purposes only.</p>
        </div>
    </footer>

    <script src="js/api.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
EOF

# normalize.css
cat > frontend/css/normalize.css << 'EOF'
/*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */

/* Document
   ========================================================================== */

/**
 * 1. Correct the line height in all browsers.
 * 2. Prevent adjustments of font size after orientation changes in iOS.
 */

html {
  line-height: 1.15; /* 1 */
  -webkit-text-size-adjust: 100%; /* 2 */
}

/* Sections
   ========================================================================== */

/**
 * Remove the margin in all browsers.
 */

body {
  margin: 0;
}

/**
 * Render the `main` element consistently in IE.
 */

main {
  display: block;
}

/**
 * Correct the font size and margin on `h1` elements within `section` and
 * `article` contexts in Chrome, Firefox, and Safari.
 */

h1 {
  font-size: 2em;
  margin: 0.67em 0;
}

/* Grouping content
   ========================================================================== */

/**
 * 1. Add the correct box sizing in Firefox.
 * 2. Show the overflow in Edge and IE.
 */

hr {
  box-sizing: content-box; /* 1 */
  height: 0; /* 1 */
  overflow: visible; /* 2 */
}

/**
 * 1. Correct the inheritance and scaling of font size in all browsers.
 * 2. Correct the odd `em` font sizing in all browsers.
 */

pre {
  font-family: monospace, monospace; /* 1 */
  font-size: 1em; /* 2 */
}

/* Text-level semantics
   ========================================================================== */

/**
 * Remove the gray background on active links in IE 10.
 */

a {
  background-color: transparent;
}

/**
 * 1. Remove the bottom border in Chrome 57-
 * 2. Add the correct text decoration in Chrome, Edge, IE, Opera, and Safari.
 */

abbr[title] {
  border-bottom: none; /* 1 */
  text-decoration: underline; /* 2 */
  text-decoration: underline dotted; /* 2 */
}

/**
 * Add the correct font weight in Chrome, Edge, and Safari.
 */

b,
strong {
  font-weight: bolder;
}

/**
 * 1. Correct the inheritance and scaling of font size in all browsers.
 * 2. Correct the odd `em` font sizing in all browsers.
 */

code,
kbd,
samp {
  font-family: monospace, monospace; /* 1 */
  font-size: 1em; /* 2 */
}

/**
 * Add the correct font size in all browsers.
 */

small {
  font-size: 80%;
}

/**
 * Prevent `sub` and `sup` elements from affecting the line height in
 * all browsers.
 */

sub,
sup {
  font-size: 75%;
  line-height: 0;
  position: relative;
  vertical-align: baseline;
}

sub {
  bottom: -0.25em;
}

sup {
  top: -0.5em;
}

/* Embedded content
   ========================================================================== */

/**
 * Remove the border on images inside links in IE 10.
 */

img {
  border-style: none;
}

/* Forms
   ========================================================================== */

/**
 * 1. Change the font styles in all browsers.
 * 2. Remove the margin in Firefox and Safari.
 */

button,
input,
optgroup,
select,
textarea {
  font-family: inherit; /* 1 */
  font-size: 100%; /* 1 */
  line-height: 1.15; /* 1 */
  margin: 0; /* 2 */
}

/**
 * Show the overflow in IE.
 * 1. Show the overflow in Edge.
 */

button,
input { /* 1 */
  overflow: visible;
}

/**
 * Remove the inheritance of text transform in Edge, Firefox, and IE.
 * 1. Remove the inheritance of text transform in Firefox.
 */

button,
select { /* 1 */
  text-transform: none;
}

/**
 * Correct the inability to style clickable types in iOS and Safari.
 */

button,
[type="button"],
[type="reset"],
[type="submit"] {
  -webkit-appearance: button;
}

/**
 * Remove the inner border and padding in Firefox.
 */

button::-moz-focus-inner,
[type="button"]::-moz-focus-inner,
[type="reset"]::-moz-focus-inner,
[type="submit"]::-moz-focus-inner {
  border-style: none;
  padding: 0;
}

/**
 * Restore the focus styles unset by the previous rule.
 */

button:-moz-focusring,
[type="button"]:-moz-focusring,
[type="reset"]:-moz-focusring,
[type="submit"]:-moz-focusring {
  outline: 1px dotted ButtonText;
}

/**
 * Correct the padding in Firefox.
 */

fieldset {
  padding: 0.35em 0.75em 0.625em;
}

/**
 * 1. Correct the text wrapping in Edge and IE.
 * 2. Correct the color inheritance from `fieldset` elements in IE.
 * 3. Remove the padding so developers are not caught out when they zero out
 *    `fieldset` elements in all browsers.
 */

legend {
  box-sizing: border-box; /* 1 */
  color: inherit; /* 2 */
  display: table; /* 1 */
  max-width: 100%; /* 1 */
  padding: 0; /* 3 */
  white-space: normal; /* 1 */
}

/**
 * Add the correct vertical alignment in Chrome, Firefox, and Opera.
 */

progress {
  vertical-align: baseline;
}

/**
 * Remove the default vertical scrollbar in IE 10+.
 */

textarea {
  overflow: auto;
}

/**
 * 1. Add the correct box sizing in IE 10.
 * 2. Remove the padding in IE 10.
 */

[type="checkbox"],
[type="radio"] {
  box-sizing: border-box; /* 1 */
  padding: 0; /* 2 */
}

/**
 * Correct the cursor style of increment and decrement buttons in Chrome.
 */

[type="number"]::-webkit-inner-spin-button,
[type="number"]::-webkit-outer-spin-button {
  height: auto;
}

/**
 * 1. Correct the odd appearance in Chrome and Safari.
 * 2. Correct the outline style in Safari.
 */

[type="search"] {
  -webkit-appearance: textfield; /* 1 */
  outline-offset: -2px; /* 2 */
}

/**
 * Remove the inner padding in Chrome and Safari on macOS.
 */

[type="search"]::-webkit-search-decoration {
  -webkit-appearance: none;
}

/**
 * 1. Correct the inability to style clickable types in iOS and Safari.
 * 2. Change font properties to `inherit` in Safari.
 */

::-webkit-file-upload-button {
  -webkit-appearance: button; /* 1 */
  font: inherit; /* 2 */
}

/* Interactive
   ========================================================================== */

/*
 * Add the correct display in Edge, IE 10+, and Firefox.
 */

details {
  display: block;
}

/*
 * Add the correct display in all browsers.
 */

summary {
  display: list-item;
}

/* Misc
   ========================================================================== */

/**
 * Add the correct display in IE 10+.
 */

template {
  display: none;
}

/**
 * Add the correct display in IE 10.
 */

[hidden] {
  display: none;
}
EOF

# styles.css
cat > frontend/css/styles.css << 'EOF'
/* QuoteMaster Enhanced Styles */

:root {
  /* Colors */
  --color-primary: #3498db;
  --color-primary-dark: #2980b9;
  --color-secondary: #2ecc71;
  --color-secondary-dark: #27ae60;
  --color-text: #333333;
  --color-text-light: #666666;
  --color-background: #f9f9f9;
  --color-card: #ffffff;
  --color-border: #e0e0e0;
  --color-error: #e74c3c;
  --color-success: #27ae60;
  --color-warning: #f39c12;
  --color-info: #3498db;
  
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-xxl: 3rem;
  
  /* Border radius */
  --border-radius: 8px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
}

/* Base Styles */
* {
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  font-family: var(--font-family);
  line-height: 1.6;
  color: var(--color-text);
  background-color: var(--color-background);
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 0;
  line-height: 1.2;
}

a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.hidden {
  display: none !important;
}

/* Header */
.site-header {
  background-color: var(--color-primary);
  color: white;
  padding: var(--spacing-lg) 0;
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.site-header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
}

.tagline {
  margin-top: var(--spacing-xs);
  font-size: 1.2rem;
  opacity: 0.9;
}

/* Cards */
.card {
  background: var(--color-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

/* Forms */
.form-section {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--color-primary-dark);
  font-weight: 600;
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
}

input[type="text"],
input[type="number"],
input[type="email"],
input[type="tel"],
select {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

input[type="text"]:focus,
input[type="number"]:focus,
input[type="email"]:focus,
input[type="tel"]:focus,
select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.help-text {
  font-size: 0.85rem;
  color: var(--color-text-light);
  margin-top: var(--spacing-xs);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.radio-option {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
}

.radio-option:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.radio-option input[type="radio"] {
  margin-right: var(--spacing-sm);
}

.radio-option label {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
  cursor: pointer;
}

.radio-option .help-text {
  margin-left: 1.5rem;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: #f1f1f1;
  color: var(--color-text);
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.form-actions {
  margin-top: var(--spacing-xl);
  text-align: center;
}

/* Quote Result */
.quote-result {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.quote-result h3 {
  margin-bottom: var(--spacing-lg);
  color: var(--color-primary);
  text-align: center;
  font-size: 1.5rem;
}

.quote-reference {
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-text-light);
  margin-bottom: var(--spacing-lg);
}

.quote-summary {
  margin-bottom: var(--spacing-xl);
}

.summary-section {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
  background-color: #f9f9f9;
  border-radius: var(--border-radius);
}

.summary-section h4 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
  font-weight: 600;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-xs);
}

.coverage-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.coverage-item {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: white;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.coverage-name {
  font-weight: 600;
}

.coverage-amount {
  font-weight: 500;
  color: var(--color-primary-dark);
}

.coverage-description {
  margin: var(--spacing-xs) 0;
  font-size: 0.9rem;
  color: var(--color-text-light);
}

.coverage-premium {
  display: block;
  text-align: right;
  font-weight: 600;
  margin-top: var(--spacing-xs);
}

.pricing-factors {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.factor {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-bottom: 1px dashed var(--color-border);
}

.factor:last-child {
  border-bottom: none;
}

.discounts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.discount-item {
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
}

.discount-item:last-child {
  border-bottom: none;
}

.discount-name {
  font-weight: 500;
}

.discount-amount {
  font-weight: 600;
  color: var(--color-success);
}

.discount-description {
  width: 100%;
  margin: var(--spacing-xs) 0 0;
  font-size: 0.85rem;
  color: var(--color-text-light);
}

.price-summary {
  background-color: #f5f9ff;
  border: 1px solid #d0e3f7;
}

.price-line {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.price-line:last-child {
  border-bottom: none;
}

.discount-line {
  color: var(--color-success);
}

.total-line {
  font-weight: 700;
  font-size: 1.2rem;
  padding: var(--spacing-md);
  background-color: #e8f4ff;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.quote-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
}

/* Loading Spinner */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: var(--spacing-xl) 0;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Features Section */
.features {
  padding: var(--spacing-xl) 0;
  text-align: center;
}

.features h2 {
  margin-bottom: var(--spacing-xl);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-xl);
}

.feature-item {
  padding: var(--spacing-lg);
  background-color: var(--color-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
}

.feature-item h3 {
  margin-bottom: var(--spacing-sm);
}

/* Footer */
.site-footer {
  background-color: #f1f1f1;
  padding: var(--spacing-xl) 0;
  margin-top: var(--spacing-xxl);
  text-align: center;
  color: var(--color-text-light);
  font-size: 0.9rem;
}

.site-footer p {
  margin: var(--spacing-xs) 0;
}

.disclaimer {
  font-style: italic;
  max-width: 600px;
  margin: var(--spacing-md) auto 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-md);
  }
  
  .card {
    padding: var(--spacing-lg);
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .pricing-factors {
    grid-template-columns: 1fr;
  }
  
  .quote-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .quote-actions .btn {
    width: 100%;
  }
}
EOF

# api.js
cat > frontend/js/api.js << 'EOF'
/**
 * API client for the QuoteMaster backend.
 * Handles all communication with the API endpoints.
 */

// Configuration
const API_CONFIG = {
    // Set the API base URL to your podman host access point
    baseUrl: 'http://localhost:8000',
    endpoints: {
        years: '/vehicle-years',
        categories: '/vehicle-categories',
        coverages: '/coverage-levels',
        maritalStatuses: '/marital-statuses',
        homeOwnership: '/home-ownership-options',
        carOwnership: '/car-ownership-options',
        vehicleValues: '/vehicle-value-ranges',
        drivingFrequency: '/driving-frequency-options',
        quote: '/calculate-quote'
    }
};

/**
 * API client object
 */
const api = {
    /**
     * Fetch options for a dropdown from the API.
     * 
     * @param {string} endpoint - The endpoint path to fetch from
     * @returns {Promise<Array>} Promise resolving to an array of options
     */
    fetchOptions: async function(endpoint) {
        try {
            console.log(`Fetching options from: ${API_CONFIG.baseUrl}/${endpoint}`);
            const response = await fetch(`${API_CONFIG.baseUrl}/${endpoint}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response not OK:', errorText);
                throw new Error(`Failed to fetch options: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`Received options for ${endpoint}:`, data);
            return data;
        } catch (error) {
            console.error(`Error fetching options from ${endpoint}:`, error);
            throw error;
        }
    },
    
    /**
     * Get available vehicle years from the API.
     * 
     * @returns {Promise<number[]>} Promise resolving to an array of years
     */
    fetchVehicleYears: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.years);
    },
    
    /**
     * Get available vehicle categories from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of categories
     */
    fetchVehicleCategories: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.categories);
    },
    
    /**
     * Get available coverage levels from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of coverage levels
     */
    fetchCoverageLevels: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.coverages);
    },
    
    /**
     * Get available marital statuses from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of marital statuses
     */
    fetchMaritalStatuses: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.maritalStatuses);
    },
    
    /**
     * Get available home ownership options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of home ownership options
     */
    fetchHomeOwnershipOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.homeOwnership);
    },
    
    /**
     * Get available car ownership options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of car ownership options
     */
    fetchCarOwnershipOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.carOwnership);
    },
    
    /**
     * Get available vehicle value ranges from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of vehicle value ranges
     */
    fetchVehicleValueRanges: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.vehicleValues);
    },
    
    /**
     * Get available driving frequency options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of driving frequency options
     */
    fetchDrivingFrequencyOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.drivingFrequency);
    },
    
    /**
     * Calculate an insurance quote based on provided parameters.
     * 
     * @param {Object} quoteParams - The quote parameters
     * @returns {Promise<Object>} Promise resolving to the quote result
     */
    calculateQuote: async function(quoteParams) {
        try {
            console.log('Sending quote request to:', `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.quote}`);
            console.log('Quote parameters:', quoteParams);
            
            const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.quote}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify(quoteParams)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.detail || `Failed to calculate quote: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Quote result:', result);
            return result;
        } catch (error) {
            console.error('Error calculating quote:', error);
            throw error;
        }
    }
};
EOF

# app.js
cat > frontend/js/app.js << 'EOF'
/**
 * QuoteMaster application main JavaScript file.
 * Handles user interactions and UI updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

/**
 * Initialize the application by setting up event listeners and loading initial data.
 */
async function initializeApp() {
    try {
        // Load all dropdown options from the API
        await Promise.all([
            loadVehicleYears(),
            loadVehicleCategories(),
            loadVehicleCoverages(),
            loadMaritalStatuses(),
            loadHomeOwnershipOptions(),
            loadCarOwnershipOptions(),
            loadVehicleValueRanges(),
            loadDrivingFrequencyOptions()
        ]);
        
        // Set up form submission handler
        const quoteForm = document.getElementById('quote-form');
        quoteForm.addEventListener('submit', handleFormSubmit);
        
        // Set up radio button styling
        setupRadioStyling();
        
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Error initializing app:', error);
        showError(`Failed to initialize application: ${error.message}`);
    }
}

/**
 * Loads available vehicle years from the API and populates the select dropdown.
 */
async function loadVehicleYears() {
    const yearSelect = document.getElementById('vehicle-year');
    await loadDropdownOptions(yearSelect, 'vehicle-years');
}

/**
 * Loads available vehicle categories from the API and populates the select dropdown.
 */
async function loadVehicleCategories() {
    const categorySelect = document.getElementById('vehicle-category');
    await loadDropdownOptions(categorySelect, 'vehicle-categories');
}

/**
 * Loads available coverage levels from the API. The radio buttons are static in the HTML.
 */
async function loadVehicleCoverages() {
    // Radio buttons are already in the HTML, nothing to load
    // But we could validate them against the API if needed
    try {
        const coverageLevels = await api.fetchCoverageLevels();
        console.log('Available coverage levels:', coverageLevels);
    } catch (error) {
        console.error('Error loading coverage levels:', error);
    }
}

/**
 * Loads available marital statuses from the API and populates the select dropdown.
 */
async function loadMaritalStatuses() {
    const maritalSelect = document.getElementById('marital-status');
    await loadDropdownOptions(maritalSelect, 'marital-statuses');
}

/**
 * Loads available home ownership options from the API and populates the select dropdown.
 */
async function loadHomeOwnershipOptions() {
    const homeOwnershipSelect = document.getElementById('home-ownership');
    await loadDropdownOptions(homeOwnershipSelect, 'home-ownership-options');
}

/**
 * Loads available car ownership options from the API and populates the select dropdown.
 */
async function loadCarOwnershipOptions() {
    const carOwnershipSelect = document.getElementById('car-ownership');
    await loadDropdownOptions(carOwnershipSelect, 'car-ownership-options');
}

/**
 * Loads available vehicle value ranges from the API and populates the select dropdown.
 */
async function loadVehicleValueRanges() {
    const vehicleValueSelect = document.getElementById('vehicle-value');
    await loadDropdownOptions(vehicleValueSelect, 'vehicle-value-ranges');
}

/**
 * Loads available driving frequency options from the API and populates the select dropdown.
 */
async function loadDrivingFrequencyOptions() {
    const drivingFrequencySelect = document.getElementById('driving-frequency');
    await loadDropdownOptions(drivingFrequencySelect, 'driving-frequency-options');
}

/**
 * Generic function to load options for a select dropdown from the API.
 * 
 * @param {HTMLSelectElement} selectElement - The select element to populate
 * @param {string} endpointPath - The API endpoint path to fetch options from
 */
async function loadDropdownOptions(selectElement, endpointPath) {
    try {
        // Show loading state
        selectElement.disabled = true;
        
        // Fetch options from API
        const options = await api.fetchOptions(endpointPath);
        
        // Clear current options (except the first one if it's a placeholder)
        const placeholderOption = selectElement.querySelector('option[value=""]');
        selectElement.innerHTML = '';
        if (placeholderOption) {
            selectElement.appendChild(placeholderOption);
        }
        
        // Add options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            selectElement.appendChild(optionElement);
        });
    } catch (error) {
        console.error(`Failed to load options for ${endpointPath}:`, error);
        showError(`Failed to load options: ${error.message}`);
    } finally {
        // Enable select regardless of success/failure
        selectElement.disabled = false;
    }
}

/**
 * Handles the form submission to calculate a quote.
 * 
 * @param {Event} event - The form submission event
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    try {
        // Get form values
        const quoteData = {
            vehicle_category: document.getElementById('vehicle-category').value,
            vehicle_year: parseInt(document.getElementById('vehicle-year').value),
            coverage_level: document.querySelector('input[name="coverage-level"]:checked').value,
            marital_status: document.getElementById('marital-status').value,
            age: parseInt(document.getElementById('driver-age').value),
            home_ownership: document.getElementById('home-ownership').value,
            car_ownership: document.getElementById('car-ownership').value,
            vehicle_value: document.getElementById('vehicle-value').value,
            driving_frequency: document.getElementById('driving-frequency').value,
            zip_code: document.getElementById('zip-code').value
        };
        
        // Validate form data
        if (!validateQuoteData(quoteData)) {
            return;
        }
        
        // Hide any previous results
        const resultElement = document.getElementById('quote-result');
        resultElement.classList.add('hidden');
        
        // Show loading spinner
        const spinner = document.getElementById('loading-spinner');
        spinner.classList.remove('hidden');
        
        // Call API to calculate the quote
        const quoteResult = await api.calculateQuote(quoteData);
        
        // Display the quote result
        displayQuoteResult(quoteResult);
    } catch (error) {
        console.error('Error calculating quote:', error);
        showError(`Failed to calculate quote: ${error.message}`);
    } finally {
        // Hide loading spinner
        document.getElementById('loading-spinner').classList.add('hidden');
    }
}

/**
 * Validates the quote request data before submission.
 * 
 * @param {Object} data - The quote data to validate
 * @returns {boolean} True if valid, false otherwise
 */
function validateQuoteData(data) {
    // Check for any empty required fields
    for (const [key, value] of Object.entries(data)) {
        if (value === "" || value === null || value === undefined) {
            showError(`Please provide a value for ${key.replace(/[_-]/g, ' ')}`);
            return false;
        }
    }
    
    // Age validation
    if (data.age < 16 || data.age > 120) {
        showError("Driver age must be between 16 and 120");
        return false;
    }
    
    // ZIP code validation
    if (!/^\d{5}$/.test(data.zip_code)) {
        showError("ZIP code must be a 5-digit number");
        return false;
    }
    
    return true;
}

/**
 * Displays the quote result in the UI.
 * 
 * @param {Object} quoteResult - The quote calculation result from the API
 */
function displayQuoteResult(quoteResult) {
    const resultElement = document.getElementById('quote-result');
    
    // Create sections for the result display
    let html = `
        <h3>Your Insurance Quote</h3>
        
        <div class="quote-summary">
            <p class="quote-reference">Quote ID: ${quoteResult.quote_id} | Valid until: ${quoteResult.expiration_date}</p>
            
            <div class="summary-section">
                <h4>Coverage Details</h4>
                <div class="coverage-list">
    `;
    
    // Add each coverage
    quoteResult.coverages.forEach(coverage => {
        html += `
            <div class="coverage-item">
                <div class="coverage-header">
                    <span class="coverage-name">${coverage.name}</span>
                    <span class="coverage-amount">${coverage.amount}</span>
                </div>
                <p class="coverage-description">${coverage.description}</p>
                <span class="coverage-premium">${coverage.premium.toFixed(2)}</span>
            </div>
        `;
    });
    
    // Add pricing factors section
    html += `
                </div>
            </div>
            
            <div class="summary-section">
                <h4>Pricing Factors</h4>
                <div class="pricing-factors">
                    <div class="factor"><span>Age Factor:</span> <strong>${quoteResult.age_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Location Factor:</span> <strong>${quoteResult.location_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Marital Status Factor:</span> <strong>${quoteResult.marital_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Vehicle Factor:</span> <strong>${quoteResult.vehicle_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Driving Frequency Factor:</span> <strong>${quoteResult.driving_factor.toFixed(2)}x</strong></div>
                </div>
            </div>
    `;
    
    // Add discounts section if there are any
    if (quoteResult.discounts && quoteResult.discounts.length > 0) {
        html += `
            <div class="summary-section">
                <h4>Your Discounts</h4>
                <div class="discounts-list">
        `;
        
        quoteResult.discounts.forEach(discount => {
            html += `
                <div class="discount-item">
                    <span class="discount-name">${discount.name}</span>
                    <span class="discount-amount">-${discount.amount.toFixed(2)}</span>
                    <p class="discount-description">${discount.description}</p>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Add final pricing section
    html += `
            <div class="summary-section price-summary">
                <div class="price-line"><span>Base Premium:</span> <span>${quoteResult.base_premium.toFixed(2)}</span></div>
                <div class="price-line"><span>Subtotal:</span> <span>${quoteResult.subtotal.toFixed(2)}</span></div>
                <div class="price-line discount-line"><span>Discounts:</span> <span>-${quoteResult.total_discounts.toFixed(2)}</span></div>
                <div class="price-line total-line"><span>Total Premium:</span> <span>${quoteResult.final_premium.toFixed(2)}</span></div>
            </div>
        </div>
        
        <div class="quote-actions">
            <button class="btn btn-primary">Purchase This Policy</button>
            <button class="btn btn-secondary" id="btn-modify-quote">Modify Quote</button>
            <button class="btn btn-secondary">Email Quote</button>
        </div>
    `;
    
    // Set the HTML content
    resultElement.innerHTML = html;
    
    // Show the result
    resultElement.classList.remove('hidden');
    
    // Add event listener to the "Modify Quote" button
    const modifyButton = document.getElementById('btn-modify-quote');
    if (modifyButton) {
        modifyButton.addEventListener('click', () => {
            resultElement.classList.add('hidden');
        });
    }
    
    // Scroll to the result
    resultElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Shows an error message to the user.
 * 
 * @param {string} message - The error message to display
 */
function showError(message) {
    alert(`Error: ${message}`);
    console.error(message);
}

/**
 * Setup styling for radio button selections to enhance usability.
 */
function setupRadioStyling() {
    const radioOptions = document.querySelectorAll('.radio-option');
    
    radioOptions.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        
        // Set initial state
        if (radio.checked) {
            option.style.borderColor = 'var(--color-primary)';
            option.style.backgroundColor = 'rgba(52, 152, 219, 0.05)';
        }
        
        // When radio is clicked, update styling
        radio.addEventListener('change', () => {
            // Reset all options
            radioOptions.forEach(opt => {
                opt.style.borderColor = 'var(--color-border)';
                opt.style.backgroundColor = '';
            });
            
            // Style the selected option
            if (radio.checked) {
                option.style.borderColor = 'var(--color-primary)';
                option.style.backgroundColor = 'rgba(52, 152, 219, 0.05)';
            }
        });
        
        // Make entire option clickable
        option.addEventListener('click', (e) => {
            if (e.target !== radio) {
                radio.checked = true;
                
                // Trigger change event to update styling
                const changeEvent = new Event('change');
                radio.dispatchEvent(changeEvent);
            }
        });
    });
}
EOF

echo -e "${GREEN}✓ Frontend files created.${NC}"
echo

# Create docker-compose.yml
echo -e "${YELLOW}Creating Docker Compose configuration...${NC}"

cat > docker-compose.yml << 'EOF'
version: '3'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend
    restart: unless-stopped

networks:
  default:
    driver: bridge
EOF

echo -e "${GREEN}✓ Docker Compose configuration created.${NC}"
echo

# Create README.md
echo -e "${YELLOW}Creating README.md...${NC}"

cat > README.md << 'EOF'
# Enhanced QuoteMaster - Car Insurance Quote Calculator

QuoteMaster is a modern web application for calculating car insurance quotes. This enhanced version includes more detailed driver and vehicle information, comprehensive coverage options, and a transparent breakdown of pricing factors.

## Features

- **Realistic Quote Calculation**: Takes into account multiple factors like:
  - Vehicle details (category, year, value, ownership)
  - Driver information (age, marital status)
  - Property details (home ownership)
  - Driving habits (frequency)
  - Location (ZIP code)

- **Detailed Coverage Information**:
  - Bodily Injury Liability
  - Property Damage Liability
  - Uninsured/Underinsured Motorist
  - Rental Car Coverage (Standard and Premium only)
  - Comprehensive and Collision (Standard and Premium only)

- **Transparent Pricing**:
  - Clear breakdown of all pricing factors
  - Detailed discount information
  - Complete premium calculation

## Tech Stack

- **Backend**:
  - Python 3.9+
  - FastAPI (modern, high-performance web framework)
  - Pydantic (data validation and settings management)
  - Uvicorn (ASGI server)

- **Frontend**:
  - HTML5
  - CSS3 (custom design system)
  - Vanilla JavaScript (no frameworks)

- **Deployment**:
  - Docker/Podman
  - Docker/Podman Compose

## Getting Started

### Prerequisites

- Docker/Podman and Docker/Podman Compose

### Quick Start

1. Start the services with Docker Compose:
   ```
   docker-compose up -d
   ```
   
   Or with Podman:
   ```
   podman-compose up -d
   ```

2. Access the application:
   - Frontend: http://localhost:8080
   - API documentation: http://localhost:8000/docs

## API Endpoints

The enhanced API includes several endpoints to support the insurance quote calculation:

- **GET /vehicle-years** - Returns available vehicle years
- **GET /vehicle-categories** - Returns available vehicle categories
- **GET /coverage-levels** - Returns available coverage levels
- **GET /marital-statuses** - Returns available marital status options
- **GET /home-ownership-options** - Returns available home ownership options
- **GET /car-ownership-options** - Returns available car ownership options
- **GET /vehicle-value-ranges** - Returns available vehicle value ranges
- **GET /driving-frequency-options** - Returns available driving frequency options
- **POST /calculate-quote** - Calculates an insurance quote based on all parameters

## Understanding the Quote Calculation

The quote calculation considers several factors:

1. **Base Premium**: Calculated from the sum of individual coverage premiums
2. **Age Factor**: Younger and elderly drivers have higher premiums
3. **Location Factor**: Based on ZIP code risk assessment
4. **Marital Factor**: Married drivers typically have lower premiums
5. **Vehicle Factor**: Based on category, year, value, and ownership
6. **Driving Frequency Factor**: More frequent driving increases premiums

Discounts are applied for:
- Home ownership
- Married status
- Experienced drivers (ages 30-65)
- Multi-policy potential
- New vehicles
- Vehicle ownership

## License

[Add your license information here]
EOF

# Make the script executable
chmod +x setup.sh

# Finish up
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}  Enhanced QuoteMaster setup completed!        ${NC}"
echo -e "${GREEN}===============================================${NC}"
echo
echo -e "To start the application with ${BLUE}${CONTAINER_CMD}${NC}:"
echo -e "  ${BLUE}${COMPOSE_CMD} up -d${NC}"
echo
echo -e "Then access:"
echo -e "  - Frontend: ${BLUE}http://localhost:8080${NC}"
echo -e "  - API docs: ${BLUE}http://localhost:8000/docs${NC}"
echo
echo -e "If you have any connectivity issues between frontend and backend:"
echo -e "  1. Edit ${BLUE}frontend/js/api.js${NC} to update the API_CONFIG.baseUrl"
echo -e "  2. You might need to use your host's IP address instead of localhost"
echo -e "  3. For Podman users, try using ${BLUE}host.containers.internal${NC} instead of localhost"
echo
echo -e "Enjoy using Enhanced QuoteMaster!"
