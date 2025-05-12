import pytest
from fastapi.testclient import TestClient
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

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
    # Set environment variables needed by the app *before* creating TestClient
    # These paths are INSIDE the container/test environment context
    os.environ["ALLOWED_PATHS"] = "/test_data"
    os.environ["READ_ONLY"] = "false"
    
    with TestClient(app) as c:
        yield c
    
    # Clean up environment variables if necessary
    del os.environ["ALLOWED_PATHS"]
    del os.environ["READ_ONLY"]

@pytest.fixture(scope="function")
def temp_fs(tmp_path_factory):
    """Create a temporary directory structure for filesystem tests."""
    # Use pytest's tmp_path_factory for reliable temp dirs
    base_dir = tmp_path_factory.mktemp("filesystem_mcp_test")
    test_data_dir = base_dir / "test_data" # Matches ALLOWED_PATHS used in client fixture
    test_data_dir.mkdir()
    
    # Create some initial files/directories
    (test_data_dir / "file1.txt").write_text("Hello from file1")
    (test_data_dir / "subdir1").mkdir()
    (test_data_dir / "subdir1" / "file2.txt").write_text("Content of file2 in subdir1")
    
    print(f"Created temp FS for testing at: {base_dir}")
    yield test_data_dir # Yield the allowed path root
    
    # Cleanup happens automatically via tmp_path_factory
    print(f"Cleaning up temp FS: {base_dir}")

# Add other fixtures if needed 