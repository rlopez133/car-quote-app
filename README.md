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
