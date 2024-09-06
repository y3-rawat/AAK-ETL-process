# Data Engineer Challenge

## Overview
This project provides a comprehensive API to fetch and manage country data from the World Bank API using FastAPI. It includes features for data caching, asynchronous processing, and a user-friendly web interface.

## Features
- Asynchronous data fetching from World Bank API
- Data caching mechanism
- RESTful API endpoints for country data
- Web interface for easy data exploration
- SQLite database for persistent storage
- Modular code structure with separation of concerns

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/y3-rawat/AAK_data_engineer_challenge.git
   ```
2. Navigate to the repository:
   ```bash
   cd AAK_data_engineer_challenge
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start the FastAPI application:
   ```bash
   uvicorn main:app --reload
   ```
2. Access the web interface at `http://127.0.0.1:8000`
3. Use the API endpoints:
   - GET `/api/country/{country_code}`: Fetch data for a specific country
   - POST `/api/country`: Save or update country data
   - DELETE `/api/country/{country_code}`: Delete data for a specific country

## API Documentation
Access the interactive API documentation at `http://127.0.0.1:8000/docs`

## Project Structure
- `main.py`: Entry point of the application
- `app/`: Main application package
  - `controllers/`: API route handlers
  - `models/`: Database models
  - `services/`: Business logic and data processing
  - `viewmodels/`: Data presentation layer
  - `database/`: Database configuration
- `static/`: Static files for the web interface
- `Database/`: JSON data storage
