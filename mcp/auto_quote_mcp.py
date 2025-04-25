"""
Enhanced Auto Insurance Quote Calculator - Model Context Protocol Server

This file implements a Model Context Protocol server for calculating auto insurance quotes.
It provides tools that AI models can use to calculate detailed car insurance quotes.
"""
import os
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, List, Optional
from enum import Enum
import hashlib
import random

# Initialize FastMCP
mcp = FastMCP("auto_quote", port=8001 )


# Enums for valid options
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

@mcp.tool()
async def get_available_years() -> List[int]:
    """
    Get a list of available vehicle years for insurance quotes.
    
    Returns:
        A list of years from current year going back 20 years.
    """
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 21, -1))
    return years

@mcp.tool()
async def get_vehicle_categories() -> List[str]:
    """
    Get a list of available vehicle categories for insurance quotes.
    
    Returns:
        A list of valid vehicle categories.
    """
    return [category.value for category in VehicleCategory]

@mcp.tool()
async def get_coverage_levels() -> List[str]:
    """
    Get a list of available coverage levels for insurance quotes.
    
    Returns:
        A list of valid coverage levels.
    """
    return [level.value for level in CoverageLevel]

@mcp.tool()
async def get_marital_statuses() -> List[str]:
    """
    Get a list of available marital statuses for insurance quotes.
    
    Returns:
        A list of valid marital statuses.
    """
    return [status.value for status in MaritalStatus]

@mcp.tool()
async def get_home_ownership_options() -> List[str]:
    """
    Get a list of available home ownership options for insurance quotes.
    
    Returns:
        A list of valid home ownership options.
    """
    return [option.value for option in HomeOwnership]

@mcp.tool()
async def get_car_ownership_options() -> List[str]:
    """
    Get a list of available car ownership options for insurance quotes.
    
    Returns:
        A list of valid car ownership options.
    """
    return [option.value for option in CarOwnership]

@mcp.tool()
async def get_vehicle_value_ranges() -> List[str]:
    """
    Get a list of available vehicle value ranges for insurance quotes.
    
    Returns:
        A list of valid vehicle value ranges.
    """
    return [value.value for value in VehicleValue]

@mcp.tool()
async def get_driving_frequency_options() -> List[str]:
    """
    Get a list of available driving frequency options for insurance quotes.
    
    Returns:
        A list of valid driving frequency options.
    """
    return [freq.value for freq in DrivingFrequency]

@mcp.tool()
async def calculate_quote(
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
    Calculate a comprehensive insurance quote based on provided parameters.
    
    Args:
        vehicle_category: Category of the vehicle (Economy, Standard, Luxury)
        vehicle_year: Manufacturing year of the vehicle
        coverage_level: Level of insurance coverage (Basic, Standard, Premium)
        marital_status: Marital status of primary driver (Single, Married, Divorced, Widowed)
        age: Age of primary driver (must be at least 16)
        home_ownership: Home ownership status (Own, Rent, Other)
        car_ownership: Car ownership status (Own, Lease, Finance)
        vehicle_value: Value range of the vehicle (Under $5,000, $5,000 - $40,000, Over $40,000)
        driving_frequency: How often the vehicle is driven (Very Little, Average, A Lot)
        zip_code: Residential ZIP code of primary driver (5-digit US ZIP code)
        
    Returns:
        A dictionary with detailed quote information including coverage details and price breakdown
    """
    # Validate parameters
    current_year = datetime.now().year
    
    # Validate age
    if age < 16 or age > 120:
        return {"error": "Driver age must be between 16 and 120"}
    
    # Validate vehicle year
    min_year = current_year - 20
    if vehicle_year < min_year or vehicle_year > current_year + 1:
        return {"error": f"Vehicle year must be between {min_year} and {current_year + 1}"}
    
    # Validate ZIP code format
    if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
        return {"error": "ZIP code must be a 5-digit number"}
    
    # Validate categorical parameters
    if vehicle_category not in [c.value for c in VehicleCategory]:
        return {"error": f"Invalid vehicle category. Valid options: {', '.join([c.value for c in VehicleCategory])}"}
    
    if coverage_level not in [c.value for c in CoverageLevel]:
        return {"error": f"Invalid coverage level. Valid options: {', '.join([c.value for c in CoverageLevel])}"}
    
    if marital_status not in [m.value for m in MaritalStatus]:
        return {"error": f"Invalid marital status. Valid options: {', '.join([m.value for m in MaritalStatus])}"}
    
    if home_ownership not in [h.value for h in HomeOwnership]:
        return {"error": f"Invalid home ownership. Valid options: {', '.join([h.value for h in HomeOwnership])}"}
    
    if car_ownership not in [c.value for c in CarOwnership]:
        return {"error": f"Invalid car ownership. Valid options: {', '.join([c.value for c in CarOwnership])}"}
    
    if vehicle_value not in [v.value for v in VehicleValue]:
        return {"error": f"Invalid vehicle value. Valid options: {', '.join([v.value for v in VehicleValue])}"}
    
    if driving_frequency not in [d.value for d in DrivingFrequency]:
        return {"error": f"Invalid driving frequency. Valid options: {', '.join([d.value for d in DrivingFrequency])}"}
    
    # Calculate coverage details
    coverages = _calculate_coverage_details(coverage_level, vehicle_value)
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
    expiration_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Return all calculation details
    return {
        "quote_details": {
            "vehicle_category": vehicle_category,
            "vehicle_year": vehicle_year,
            "coverage_level": coverage_level,
            "marital_status": marital_status,
            "age": age,
            "home_ownership": home_ownership,
            "car_ownership": car_ownership,
            "vehicle_value": vehicle_value,
            "driving_frequency": driving_frequency,
            "zip_code": zip_code
        },
        "coverages": coverages,
        "pricing_factors": {
            "base_premium": round(base_premium, 2),
            "age_factor": round(age_factor, 2),
            "location_factor": round(location_factor, 2),
            "marital_factor": round(marital_factor, 2),
            "vehicle_factor": round(vehicle_factor, 2),
            "driving_factor": round(driving_factor, 2)
        },
        "discounts": discounts,
        "pricing_summary": {
            "subtotal": round(adjusted_premium, 2),
            "total_discounts": round(total_discounts, 2),
            "final_premium": round(final_premium, 2)
        },
        "quote_reference": {
            "quote_id": quote_id,
            "expiration_date": expiration_date,
            "generated_at": datetime.now().isoformat()
        }
    }

@mcp.tool()
async def get_coverage_explanation(coverage_level: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed explanations of what each coverage protects and the coverage limits by level.
    
    Args:
        coverage_level: Optional specific coverage level to explain (Basic, Standard, Premium)
    
    Returns:
        Detailed explanation of coverages
    """
    all_coverage_info = {
        "Bodily Injury Liability": {
            "description": "Covers costs if you injure someone else in a car accident. This helps pay for their medical expenses, lost wages, pain and suffering, and legal fees if they sue you.",
            "limits": {
                "Basic": "$15,000 per person/$30,000 per accident",
                "Standard": "$50,000 per person/$100,000 per accident",
                "Premium": "$100,000 per person/$300,000 per accident"
            }
        },
        "Property Damage Liability": {
            "description": "Covers damage you cause to other people's property, including their vehicles, buildings, fences, etc. Also covers legal defense costs if you're sued.",
            "limits": {
                "Basic": "$5,000 per accident",
                "Standard": "$25,000 per accident",
                "Premium": "$50,000 per accident"
            }
        },
        "Uninsured/Underinsured Motorist": {
            "description": "Protects you and your passengers if injured by a driver who has insufficient or no insurance. Covers medical bills, lost wages, and pain and suffering.",
            "limits": {
                "Basic": "$15,000 per person/$30,000 per accident",
                "Standard": "$50,000 per person/$100,000 per accident",
                "Premium": "$100,000 per person/$300,000 per accident"
            }
        },
        "Rental Car Coverage": {
            "description": "Pays for a rental car while your vehicle is being repaired after a covered accident.",
            "limits": {
                "Basic": "Not included",
                "Standard": "$25 per day, up to $750 maximum",
                "Premium": "$30 per day, up to $900 maximum"
            }
        },
        "Comprehensive": {
            "description": "Covers damage to your car from non-collision events like theft, vandalism, fire, natural disasters, falling objects, or hitting an animal.",
            "limits": {
                "Basic": "Not included",
                "Standard": "$500 deductible",
                "Premium": "$250 deductible"
            }
        },
        "Collision": {
            "description": "Covers damage to your car from a collision with another vehicle or object, regardless of who is at fault.",
            "limits": {
                "Basic": "Not included",
                "Standard": "$500 deductible",
                "Premium": "$250 deductible"
            }
        }
    }
    
    # If a specific coverage level is requested, filter the information
    if coverage_level:
        if coverage_level not in [c.value for c in CoverageLevel]:
            return {"error": f"Invalid coverage level. Valid options: {', '.join([c.value for c in CoverageLevel])}"}
        
        result = {"coverage_level": coverage_level, "coverages": {}}
        
        for coverage_name, coverage_info in all_coverage_info.items():
            # Skip coverages not included in the requested level
            limit = coverage_info["limits"].get(coverage_level, "Not included")
            if limit == "Not included" and coverage_level == "Basic":
                continue
                
            result["coverages"][coverage_name] = {
                "description": coverage_info["description"],
                "limit": limit
            }
        
        return result
    
    # Otherwise return all information
    return {
        "coverage_levels": {
            "Basic": "Minimal coverage that meets state requirements. Higher out-of-pocket costs if you have an accident.",
            "Standard": "Balanced coverage with moderate out-of-pocket costs. Includes comprehensive and collision.",
            "Premium": "Maximum protection with lowest out-of-pocket costs. Includes all available coverages with higher limits."
        },
        "coverages": all_coverage_info
    }

@mcp.tool()
async def get_pricing_factors_explanation() -> Dict[str, Any]:
    """
    Get detailed explanations of all the factors that affect insurance pricing.
    
    Returns:
        Detailed explanation of pricing factors
    """
    return {
        "age_factors": {
            "description": "Driver age significantly impacts insurance rates due to risk correlation.",
            "brackets": {
                "Under 20": "2.0x (highest risk)",
                "20-24": "1.5x (high risk)",
                "25-29": "1.2x (moderate risk)",
                "30-59": "1.0x (base rate)",
                "60-69": "1.1x (slightly elevated risk)",
                "70+": "1.3x (higher risk)"
            }
        },
        "location_factors": {
            "description": "ZIP codes affect rates based on local accident rates, theft statistics, population density, and weather patterns.",
            "impact": "Can vary premiums by -20% to +50% depending on location risk assessment."
        },
        "marital_status_factors": {
            "description": "Statistics show married drivers have fewer accidents on average.",
            "impact": {
                "Single": "1.1x (slightly higher risk)",
                "Married": "0.9x (lower risk)",
                "Divorced": "1.0x (base rate)",
                "Widowed": "0.95x (slightly lower risk)"
            }
        },
        "vehicle_factors": {
            "category_impact": {
                "Economy": "0.9x (lower repair/replacement costs)",
                "Standard": "1.0x (base rate)",
                "Luxury": "1.3x (higher repair/replacement costs)"
            },
            "age_impact": "Newer vehicles cost more to insure, with premium decreasing ~3% per year of age",
            "value_impact": {
                "Under $5,000": "0.8x (lower replacement cost)",
                "$5,000 - $40,000": "1.0x (base rate)",
                "Over $40,000": "1.3x (higher replacement cost)"
            },
            "ownership_impact": {
                "Own": "0.95x (slight discount)",
                "Finance": "1.0x (base rate)",
                "Lease": "1.05x (slight increase)"
            }
        },
        "driving_frequency_factors": {
            "description": "More time on the road increases exposure to potential accidents.",
            "impact": {
                "Very Little": "0.8x (lower exposure)",
                "Average": "1.0x (base rate)",
                "A Lot": "1.2x (higher exposure)"
            }
        }
    }

@mcp.tool()
async def get_discount_explanations() -> Dict[str, Any]:
    """
    Get detailed explanations of all potential discounts.
    
    Returns:
        Detailed explanation of available discounts
    """
    return {
        "Homeowner Discount": {
            "description": "Discount for customers who own their home. Statistics show homeowners file fewer claims.",
            "eligibility": "Must own your home (not renting or other arrangement).",
            "typical_amount": "$75.00"
        },
        "Married Driver Discount": {
            "description": "Discount for married drivers, who statistically file fewer claims.",
            "eligibility": "Must have marital status of 'Married'.",
            "typical_amount": "$50.00"
        },
        "Experienced Driver Discount": {
            "description": "Discount for drivers in the age range with the best safety records.",
            "eligibility": "Driver must be between 30-65 years old.",
            "typical_amount": "$40.00"
        },
        "Multi-Policy Discount": {
            "description": "Discount for bundling multiple insurance policies with the same company.",
            "eligibility": "Must own home and have Premium coverage level (indicating interest in comprehensive coverage).",
            "typical_amount": "$100.00"
        },
        "New Vehicle Discount": {
            "description": "Discount for newer vehicles with modern safety features.",
            "eligibility": "Vehicle must be 3 years old or newer.",
            "typical_amount": "$60.00"
        },
        "Vehicle Owner Discount": {
            "description": "Discount for customers who own their vehicles outright.",
            "eligibility": "Vehicle ownership status must be 'Own' (not leased or financed).",
            "typical_amount": "$30.00"
        }
    }

@mcp.tool()
async def sample_quote_request() -> Dict[str, Any]:
    """
    Generate a sample insurance quote request with typical parameters.
    
    Returns:
        A sample quote request as a dictionary
    """
    current_year = datetime.now().year
    return {
        "vehicle_category": "Standard",
        "vehicle_year": current_year - 3,  # 3-year-old car
        "coverage_level": "Standard",
        "marital_status": "Married",
        "age": 35,
        "home_ownership": "Own",
        "car_ownership": "Finance",
        "vehicle_value": "$5,000 - $40,000",
        "driving_frequency": "Average",
        "zip_code": "90210"  # Beverly Hills!
    }

# Internal helper functions for the insurance calculator
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

if __name__ == "__main__":
    mcp.run(transport="sse")
