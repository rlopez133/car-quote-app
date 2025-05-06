"""
QuoteMaster API - Model Context Protocol Server

This file implements a Model Context Protocol server for the QuoteMaster API.
It provides tools that AI models can use to calculate detailed car insurance quotes.
"""
import os
from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime

# Initialize FastMCP
mcp = FastMCP("quote_master", port=8001)

# Define the API base URL
BACKEND_URL = os.getenv("BACKEND_URL","http://localhost:8000")

# Parameter Options Retrieval Tools
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
    customer_name: str,
    vehicle_category: str,
    vehicle_year: int,
    coverage_level: str,
    marital_status: str,
    age: int,
    home_ownership: str,
    car_ownership: str,
    vehicle_value: str,
    driving_frequency: str,
    #zip_code: str
) -> Dict[str, Any]:
    """
    Calculate a comprehensive insurance quote based on provided parameters.
    
    Args:
        customer_name: The customers name. If unknown use "John Doe"
        vehicle_category: Category of the vehicle (Economy, Standard, Luxury)
        vehicle_year: Manufacturing year of the vehicle
        coverage_level: Level of insurance coverage (Basic, Standard, Premium)
        marital_status: Marital status of primary driver (Single, Married, Divorced, Widowed)
        age: Age of primary driver (must be at least 16)
        home_ownership: Home ownership status (Own, Rent, Other)
        car_ownership: Car ownership status (Own, Lease, Finance)
        vehicle_value: Value range of the vehicle (Under $5,000, $5,000 - $40,000, Over $40,000)
        driving_frequency: How often the vehicle is driven (Very Little, Average, A Lot)
        
    Returns:
        A dictionary with detailed quote information including coverage details and price breakdown
    """
    try:
        # Input validation
        if age < 16:
            return {"error": "Driver must be at least 16 years old"}
        
        # if not (zip_code.isdigit() and len(zip_code) == 5):
        #     return {"error": "ZIP code must be a 5-digit number"}
        
        # Prepare the request payload
        quote_request = {
            "customer_name": customer_name,
            "vehicle_category": vehicle_category,
            "vehicle_year": vehicle_year,
            "coverage_level": coverage_level,
            "marital_status": marital_status,
            "age": age,
            "home_ownership": home_ownership,
            "car_ownership": car_ownership,
            "vehicle_value": vehicle_value,
            "driving_frequency": driving_frequency,
            "zip_code": "90210"
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


# Run the MCP server when this script is executed directly
if __name__ == "__main__":
    print(f"Starting QuoteMaster API MCP server")
    mcp.run(transport="sse")