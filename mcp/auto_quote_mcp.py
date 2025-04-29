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
import requests
import json

# Initialize FastMCP
mcp = FastMCP("auto_quote", port=8001 )

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/")

@mcp.tool()
async def get_quotes() -> List[Dict[str, Any]]:
    """
    Get a list of all quotes currently in the system.
    
    Returns:
        A list of quote objects.
    """

    response = requests.get(f"{BACKEND_URL}/api/quotes")
    return json.loads(response.content)


@mcp.tool()
async def get_quote(quote_id: str) -> Dict[str, Any]:
    """
    Get details for a specific quote.
    
    Args:
        quote_id: The ID of the quote to retrieve
        
    Returns:
        A quote object or error if not found.
    """
    response = requests.get(f"{BACKEND_URL}/api/quotes/{quote_id}")
    return json.loads(response.content)


@mcp.tool()
async def update_quote(
    id: Optional[str] = "Q1",
    customer: Optional[str] = "Full Name",
    email: Optional[str] = "FullName@RedHat.com",
    phone: Optional[str] = "555-555-5555",
    vehicle: Optional[str] = "2099 Flying Car",
    coverage : Optional[str] =  "Basic",
) -> Dict[str, Any]:
    """
    Add a new quote to the system.
    
    Args:
        id: Q1001
        Customer: Full Name
        email: an Email address
        phone: 555-555-5555
        vehicle: 2099 Flying Car
        coverage: Basic
        
    Returns:
        Success or error message
    """

    quote_data = {}

    # Set defaults for optional fields

    quote_data["date"] = datetime.now().strftime("%Y-%m-%d")
    quote_data["status"] = quote_data.get("status", "new")
    
    quote_data["customer"] = customer
    quote_data["email"] = email
    quote_data["phone"] = phone
    quote_data["vehicle"] = vehicle 
    quote_data["coverage"] = coverage
    
    response = requests.post(f"{BACKEND_URL}/api/quotes/{id}",
                             json=quote_data)
    print(quote_data)
    if response == "200":
        return {"success": True, "message": f"Quote {id} added successfully", "quote_id": id}
    else:
        return {"fail": True, "message": response.content}

@mcp.tool()
async def delete_quote(quote_id: str) -> Dict[str, Any]:
    """
    Delete a quote from the system.
    
    Args:
        quote_id: The ID of the quote to delete
        
    Returns:
        Success or error message
    """
    quotes_path = "/app/data/quotes.json"
    quotes = await get_quotes()
    
    # Find the quote index
    quote_index = next((i for i, q in enumerate(quotes) if q["id"] == quote_id), None)
    
    if quote_index is None:
        return {"error": f"Quote {quote_id} not found"}
    
    # Remove the quote
    removed_quote = quotes.pop(quote_index)
    
    # Save back to file
    with open(quotes_path, "w") as f:
        json.dump(quotes, f, indent=2)
    
    return {"success": True, "message": f"Quote {quote_id} deleted successfully"}

if __name__ == "__main__":
    mcp.run(transport="sse")
