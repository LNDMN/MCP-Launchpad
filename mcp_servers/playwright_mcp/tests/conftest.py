import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path to allow imports
# This assumes tests are run from the playwright_mcp directory or its parent
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

try:
    # Attempt to import the app from the main module
    from main import app
except ImportError as e:
    print(f"Error importing FastAPI app: {e}")
    print(f"sys.path: {sys.path}")
    # Define a dummy app if import fails, so tests can be discovered
    # but actual tests requiring the client will fail clearly.
    from fastapi import FastAPI
    app = FastAPI(title="Dummy App - Import Failed")

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as c:
        yield c

# Add other common fixtures here, e.g., for setup/teardown 