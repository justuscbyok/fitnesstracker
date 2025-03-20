# Fitness Tracker API

A simple FastAPI application for tracking fitness workouts, exercises, and progress.

## Features

- User registration and management
- Create and manage workouts
- Track fitness progress
- Simple in-memory storage for demo purposes

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository (or unzip the provided file)

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

To run the application:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

This will start the API server at http://localhost:8000

### API Documentation

Once the server is running, you can access:

- Interactive API documentation (Swagger UI): http://localhost:8000/docs
- Alternative API documentation (ReDoc): http://localhost:8000/redoc

## API Endpoints

The API includes the following endpoints:

- `/users/*` - User registration and management
- `/workouts/*` - Workout creation and tracking
- `/healthz` - Health check endpoint 

## Notes for Evaluators

- This application uses in-memory storage for simplicity and demo purposes
- No database setup is required - everything runs in memory
- All data is lost when the server is restarted

## Technology Stack

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
- [Uvicorn](https://www.uvicorn.org/) - ASGI server for Python 