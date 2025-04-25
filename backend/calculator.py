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
