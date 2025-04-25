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
