"""
Pytest configuration and fixtures for API tests.
Provides TestClient and test data fixtures using the AAA pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture: Provides a TestClient for making requests to the FastAPI app.
    
    The TestClient handles the HTTP communication with the app without
    needing a running server.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture: Provides a fresh copy of test activities.
    
    This creates a clean state for each test to prevent data pollution
    between tests.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
