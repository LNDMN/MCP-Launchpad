import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

# Mock the GITHUB_TOKEN environment variable for testing
# WARNING: Do NOT commit real tokens! Use a fake one for local tests.
# In CI/CD, this should be securely injected.
MOCK_TOKEN = "ghp_FAKE_TOKEN_FOR_TESTING_ONLY_12345"
os.environ["GITHUB_TOKEN"] = MOCK_TOKEN 

try:
    from main import app
except ImportError as e:
    print(f"Error importing FastAPI app: {e}")
    print(f"sys.path: {sys.path}")
    from fastapi import FastAPI
    app = FastAPI(title="Dummy App - Import Failed")

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    # Ensure the mock token is set before creating the client
    if os.environ.get("GITHUB_TOKEN") != MOCK_TOKEN:
         print("Warning: Mock GITHUB_TOKEN not set correctly for test client!")
         # os.environ["GITHUB_TOKEN"] = MOCK_TOKEN # Optionally force set it again
    
    with TestClient(app) as c:
        yield c
    
    # Clean up environment variable after tests if needed (though setting it globally might be ok for tests)
    # del os.environ["GITHUB_TOKEN"]

# Add other common fixtures if needed 