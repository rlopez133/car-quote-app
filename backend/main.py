"""
QuoteMaster API - Model Context Protocol Server

This file implements a Model Context Protocol server for the QuoteMaster API.
It provides tools that AI models can use to calculate detailed car insurance quotes.
"""
import os
from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime, timedelta
import uuid

# Initialize FastMCP
mcp = FastMCP("quote_master", port=8001)

# Define the API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://car-quote-app-backend-insurance-app.apps.ocp-beta-test.nerc.mghpcc.org")

# Parameter Options Retrieval Tools
@mcp.tool()
async def get_available_years() -> List[int]:
    """
    Get a list of available vehicle years for insurance quotes.
    
    Returns:
        A list of years from current year going back 20 years.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-years")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get available years: {str(e)}"}

@mcp.tool()
async def get_vehicle_categories() -> List[str]:
    """
    Get a list of available vehicle categories for insurance quotes.
    
    Returns:
        A list of valid vehicle categories.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-categories")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get vehicle categories: {str(e)}"}

@mcp.tool()
async def get_coverage_levels() -> List[str]:
    """
    Get a list of available coverage levels for insurance quotes.
    
    Returns:
        A list of valid coverage levels.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/coverage-levels")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get coverage levels: {str(e)}"}

@mcp.tool()
async def get_marital_statuses() -> List[str]:
    """
    Get a list of available marital statuses for insurance quotes.
    
    Returns:
        A list of valid marital statuses.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/marital-statuses")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get marital statuses: {str(e)}"}

@mcp.tool()
async def get_home_ownership_options() -> List[str]:
    """
    Get a list of available home ownership options for insurance quotes.
    
    Returns:
        A list of valid home ownership options.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/home-ownership-options")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get home ownership options: {str(e)}"}

@mcp.tool()
async def get_car_ownership_options() -> List[str]:
    """
    Get a list of available car ownership options for insurance quotes.
    
    Returns:
        A list of valid car ownership options.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/car-ownership-options")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get car ownership options: {str(e)}"}

@mcp.tool()
async def get_vehicle_value_ranges() -> List[str]:
    """
    Get a list of available vehicle value ranges for insurance quotes.
    
    Returns:
        A list of valid vehicle value ranges.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/vehicle-value-ranges")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get vehicle value ranges: {str(e)}"}

@mcp.tool()
async def get_driving_frequency_options() -> List[str]:
    """
    Get a list of available driving frequency options for insurance quotes.
    
    Returns:
        A list of valid driving frequency options.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/driving-frequency-options")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to get driving frequency options: {str(e)}"}

# Quote Management Tools
@mcp.tool()
async def list_quotes() -> List[Dict[str, Any]]:
    """
    Get all quotes currently in the system.
    
    Returns:
        A list of quote objects.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/api/quotes")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to list quotes: {str(e)}"}

@mcp.tool()
async def get_quote(quote_id: str) -> Dict[str, Any]:
    """
    Get details for a specific quote.
    
    Args:
        quote_id: The ID of the quote to retrieve
        
    Returns:
        A quote object or error if not found.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/api/quotes/{quote_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Quote {quote_id} not found"}
        return {"error": f"Failed to get quote: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to get quote: {str(e)}"}

@mcp.tool()
async def update_quote(
    quote_id: str,
    customer: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    vehicle: Optional[str] = None,
    coverage: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing quote in the system.
    
    Args:
        quote_id: The ID of the quote to update
        customer: Customer name
        email: Customer email address
        phone: Customer phone number
        vehicle: Vehicle description
        coverage: Coverage level (Basic, Standard, Premium)
        status: Quote status
        date: Quote date
        
    Returns:
        Success or error message
    """
    try:
        # Build update payload with only provided fields
        update_data = {}
        if customer is not None:
            update_data["customer"] = customer
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if vehicle is not None:
            update_data["vehicle"] = vehicle
        if coverage is not None:
            update_data["coverage"] = coverage
        if status is not None:
            update_data["status"] = status
        if date is not None:
            update_data["date"] = date
        elif update_data:  # Only add date if we're making other updates
            update_data["date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Send update request
        response = requests.post(f"{BACKEND_URL}/api/quotes/{quote_id}", json=update_data)
        response.raise_for_status()
        
        return {"success": True, "message": f"Quote {quote_id} updated successfully"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Quote {quote_id} not found"}
        return {"error": f"Failed to update quote: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to update quote: {str(e)}"}

@mcp.tool()
async def add_quote(
    customer: str,
    email: str,
    phone: str,
    vehicle: str,
    coverage: str,
    status: str = "new",
    premium: Optional[str] = None,
    quote_id: Optional[str] = None,
    zip_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a new quote to the system.
    
    Args:
        customer: Customer name
        email: Customer email address
        phone: Customer phone number
        vehicle: Vehicle description (e.g., "2023 Toyota Camry (Standard)")
        coverage: Coverage level (Basic, Standard, Premium)
        status: Quote status (default: "new")
        premium: Premium amount (formatted as string, e.g., "$1,250.00")
        quote_id: Optional custom ID for the quote (system will generate one if not provided)
        zip_code: Optional ZIP code for the customer
        
    Returns:
        Success or error message with the quote ID
    """
    try:
        # Get existing quotes to find the next available ID
        quotes = await list_quotes()
        if isinstance(quotes, dict) and "error" in quotes:
            return quotes  # Return the error
            
        # Generate a new quote ID if not provided
        if not quote_id:
            # Find the highest existing quote number
            existing_ids = [q.get("id", "Q0") for q in quotes if isinstance(q, dict)]
            numeric_parts = [int(qid.replace("Q", "")) for qid in existing_ids if qid.startswith("Q") and qid[1:].isdigit()]
            next_number = max(numeric_parts, default=1000) + 1
            quote_id = f"Q{next_number}"
        
        # Create the quote data
        quote_data = {
            "customer": customer,
            "email": email,
            "phone": phone,
            "vehicle": vehicle,
            "coverage": coverage,
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add optional fields if provided
        if premium:
            quote_data["premium"] = premium
        if zip_code:
            quote_data["zip"] = zip_code
        
        # Save the quote by using the API's update endpoint (which creates if not exists)
        response = requests.post(f"{BACKEND_URL}/api/quotes/{quote_id}", json=quote_data)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Quote {quote_id} created successfully",
            "quote_id": quote_id
        }
    except Exception as e:
        return {"error": f"Failed to add quote: {str(e)}"}

@mcp.tool()
async def send_quote_email(
    quote_id: str,
    subject: str = "Your Insurance Quote",
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email with quote information.
    
    Args:
        quote_id: The ID of the quote to email
        subject: Email subject line
        message: Custom message to include in the email
        
    Returns:
        Success or error message
    """
    try:
        email_data = {
            "quote_id": quote_id,
            "subject": subject
        }
        if message:
            email_data["message"] = message
            
        response = requests.post(f"{BACKEND_URL}/api/quotes/{quote_id}/email", json=email_data)
        response.raise_for_status()
        
        return {"success": True, "message": f"Quote email sent successfully for {quote_id}"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Quote {quote_id} not found"}
        return {"error": f"Failed to send quote email: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to send quote email: {str(e)}"}

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
    try:
        # Input validation
        if age < 16:
            return {"error": "Driver must be at least 16 years old"}
        
        if not (zip_code.isdigit() and len(zip_code) == 5):
            return {"error": "ZIP code must be a 5-digit number"}
        
        # Prepare the request payload
        quote_request = {
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
        }
        
        # Make API request to calculate quote
        response = requests.post(f"{BACKEND_URL}/calculate-quote", json=quote_request)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.text if hasattr(e, 'response') and hasattr(e.response, 'text') else str(e)
        return {"error": f"Failed to calculate quote: {error_detail}"}
    except Exception as e:
        return {"error": f"Failed to calculate quote: {str(e)}"}

@mcp.tool()
async def calculate_and_save_quote(
    # Quote calculation parameters
    vehicle_category: str,
    vehicle_year: int,
    coverage_level: str,
    marital_status: str,
    age: int,
    home_ownership: str,
    car_ownership: str,
    vehicle_value: str,
    driving_frequency: str,
    zip_code: str,
    # Customer information
    customer: str,
    email: str,
    phone: str,
    status: str = "new"
) -> Dict[str, Any]:
    """
    Calculate a quote and save it to the system in one operation.
    
    Args:
        # Quote calculation parameters
        vehicle_category: Category of the vehicle (Economy, Standard, Luxury)
        vehicle_year: Manufacturing year of the vehicle
        coverage_level: Level of insurance coverage (Basic, Standard, Premium)
        marital_status: Marital status of primary driver
        age: Age of primary driver (must be at least 16)
        home_ownership: Home ownership status (Own, Rent, Other)
        car_ownership: Car ownership status (Own, Lease, Finance)
        vehicle_value: Value range of the vehicle
        driving_frequency: How often the vehicle is driven
        zip_code: Residential ZIP code of primary driver
        # Customer information
        customer: Customer name
        email: Customer email address
        phone: Customer phone number
        status: Quote status (default: "new")
        
    Returns:
        A dictionary with detailed quote information and the saved quote ID
    """
    try:
        # First calculate the quote
        quote_result = await calculate_quote(
            vehicle_category=vehicle_category,
            vehicle_year=vehicle_year,
            coverage_level=coverage_level,
            marital_status=marital_status,
            age=age,
            home_ownership=home_ownership,
            car_ownership=car_ownership,
            vehicle_value=vehicle_value,
            driving_frequency=driving_frequency,
            zip_code=zip_code
        )
        
        # Check if quote calculation was successful
        if isinstance(quote_result, dict) and "error" in quote_result:
            return quote_result  # Return the error
        
        # Format vehicle description
        vehicle_description = f"{vehicle_year} {vehicle_category} Vehicle"
        
        # Format premium as a string with dollar sign
        premium_formatted = f"${quote_result.get('final_premium', 0):.2f}"
        
        # Now save the quote
        save_result = await add_quote(
            customer=customer,
            email=email,
            phone=phone,
            vehicle=vehicle_description,
            coverage=coverage_level,
            status=status,
            premium=premium_formatted,
            zip_code=zip_code
        )
        
        # Check if saving was successful
        if isinstance(save_result, dict) and "error" in save_result:
            return {
                "error": save_result["error"],
                "quote_calculation": quote_result  # Return the calculated quote even if saving failed
            }
        
        # Return combined result
        return {
            "success": True,
            "message": f"Quote calculated and saved successfully",
            "quote_id": save_result.get("quote_id"),
            "quote_details": quote_result
        }
    except Exception as e:
        return {"error": f"Failed to calculate and save quote: {str(e)}"}

# Run the MCP server when this script is executed directly
if __name__ == "__main__":
    print(f"Starting QuoteMaster API MCP server on port 8001")
    mcp.run(transport="sse")
