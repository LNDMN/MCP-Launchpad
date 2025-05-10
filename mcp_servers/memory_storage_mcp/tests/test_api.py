#!/usr/bin/env python3
"""
Memory Storage MCP - API Tests

This module contains tests for the Memory Storage MCP API.
It uses pytest and the FastAPI TestClient to test the API endpoints.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Generator, Optional

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

# Add parent directory to path to import app
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import app from parent directory
from app import app, DATA_DIR, get_project_path, get_file_path

# Test models with strict typing
class ProjectResponse(BaseModel):
    name: str
    created_at: str
    file_count: int

class FileResponse(BaseModel):
    name: str
    size: int
    last_modified: str

class FileContentResponse(BaseModel):
    name: str
    content: str
    size: int
    last_modified: str

class SuccessResponse(BaseModel):
    status: str
    message: str

class A2AResponse(BaseModel):
    status: str
    content: Optional[str] = None
    message: Optional[str] = None
    projects: Optional[List[str]] = None
    files: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

# Fixtures
@pytest.fixture(scope="module")
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    old_data_dir = os.environ.get("MEMORY_STORAGE_DATA_DIR")
    
    # Set environment variable for DATA_DIR
    os.environ["MEMORY_STORAGE_DATA_DIR"] = str(temp_dir)
    
    # Override app's DATA_DIR (this is a bit of a hack, but it works)
    app.dependency_overrides = {}
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    if old_data_dir:
        os.environ["MEMORY_STORAGE_DATA_DIR"] = old_data_dir

@pytest.fixture(scope="module")
def client(temp_data_dir: Path) -> TestClient:
    """Get a TestClient instance."""
    with TestClient(app) as client:
        yield client

# Tests
def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["status"] == "Memory Storage MCP is running"

def test_project_crud(client: TestClient, temp_data_dir: Path) -> None:
    """Test project CRUD operations."""
    
    # Create project
    project_name = "test_project"
    response = client.post("/projects", json={"name": project_name})
    assert response.status_code == 200
    data = response.json()
    assert SuccessResponse(**data)
    assert data["status"] == "success"
    assert project_name in data["message"]
    
    # Verify project directory was created
    project_dir = temp_data_dir / project_name
    assert project_dir.exists()
    assert project_dir.is_dir()
    
    # List projects
    response = client.get("/projects")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) >= 1
    for project in projects:
        assert ProjectResponse(**project)
    project_names = [p["name"] for p in projects]
    assert project_name in project_names
    
    # Get project
    response = client.get(f"/projects/{project_name}")
    assert response.status_code == 200
    project = response.json()
    assert ProjectResponse(**project)
    assert project["name"] == project_name
    assert project["file_count"] == 0
    
    # Delete project
    response = client.delete(f"/projects/{project_name}")
    assert response.status_code == 200
    data = response.json()
    assert SuccessResponse(**data)
    assert data["status"] == "success"
    assert project_name in data["message"]
    
    # Verify project was deleted
    assert not project_dir.exists()

def test_file_crud(client: TestClient, temp_data_dir: Path) -> None:
    """Test file CRUD operations."""
    
    # Create project for testing files
    project_name = "test_file_project"
    client.post("/projects", json={"name": project_name})
    
    # Create file
    file_name = "test_file.md"
    file_content = "# Test Content\n\nThis is a test file."
    response = client.post(
        f"/projects/{project_name}/files",
        json={"name": file_name, "content": file_content}
    )
    assert response.status_code == 200
    data = response.json()
    assert SuccessResponse(**data)
    assert data["status"] == "success"
    assert file_name in data["message"]
    
    # Verify file was created
    file_path = temp_data_dir / project_name / file_name
    assert file_path.exists()
    assert file_path.is_file()
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == file_content
    
    # List files
    response = client.get(f"/projects/{project_name}/files")
    assert response.status_code == 200
    files = response.json()
    assert isinstance(files, list)
    assert len(files) == 1
    for file in files:
        assert FileResponse(**file)
    assert files[0]["name"] == file_name
    
    # Read file
    response = client.get(f"/projects/{project_name}/files/{file_name}")
    assert response.status_code == 200
    file_data = response.json()
    assert FileContentResponse(**file_data)
    assert file_data["name"] == file_name
    assert file_data["content"] == file_content
    
    # Update file
    updated_content = "# Updated Content\n\nThis file has been updated."
    response = client.put(
        f"/projects/{project_name}/files/{file_name}",
        json={"content": updated_content}
    )
    assert response.status_code == 200
    data = response.json()
    assert SuccessResponse(**data)
    assert data["status"] == "success"
    assert "updated" in data["message"]
    
    # Verify file was updated
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == updated_content
    
    # Read updated file
    response = client.get(f"/projects/{project_name}/files/{file_name}")
    assert response.status_code == 200
    file_data = response.json()
    assert file_data["content"] == updated_content
    
    # Delete file
    response = client.delete(f"/projects/{project_name}/files/{file_name}")
    assert response.status_code == 200
    data = response.json()
    assert SuccessResponse(**data)
    assert data["status"] == "success"
    assert "deleted" in data["message"]
    
    # Verify file was deleted
    assert not file_path.exists()
    
    # Clean up project
    client.delete(f"/projects/{project_name}")

def test_a2a_endpoint(client: TestClient, temp_data_dir: Path) -> None:
    """Test A2A compatibility endpoint."""
    
    # Create project for A2A testing
    project_name = "test_a2a_project"
    client.post("/projects", json={"name": project_name})
    
    # Test list_projects action
    response = client.post("/a2a", json={
        "action": "list_projects",
        "parameters": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert A2AResponse(**data)
    assert data["status"] == "success"
    assert project_name in data["projects"]
    
    # Create a file using memory_bank_write
    file_name = "a2a_test_file.md"
    file_content = "# A2A Test File\n\nCreated through the A2A endpoint."
    response = client.post("/a2a", json={
        "action": "memory_bank_write",
        "parameters": {
            "projectName": project_name,
            "fileName": file_name,
            "content": file_content
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert A2AResponse(**data)
    assert data["status"] == "success"
    assert "written" in data["message"]
    
    # Verify file exists
    file_path = temp_data_dir / project_name / file_name
    assert file_path.exists()
    
    # Test list_project_files action
    response = client.post("/a2a", json={
        "action": "list_project_files",
        "parameters": {"projectName": project_name}
    })
    assert response.status_code == 200
    data = response.json()
    assert A2AResponse(**data)
    assert data["status"] == "success"
    assert file_name in data["files"]
    
    # Test memory_bank_read action
    response = client.post("/a2a", json={
        "action": "memory_bank_read",
        "parameters": {
            "projectName": project_name,
            "fileName": file_name
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert A2AResponse(**data)
    assert data["status"] == "success"
    assert data["content"] == file_content
    assert "metadata" in data
    assert "lastModified" in data["metadata"]
    assert "size" in data["metadata"]
    
    # Test memory_bank_update action
    updated_content = "# Updated A2A Test File\n\nUpdated through the A2A endpoint."
    response = client.post("/a2a", json={
        "action": "memory_bank_update",
        "parameters": {
            "projectName": project_name,
            "fileName": file_name,
            "content": updated_content
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert A2AResponse(**data)
    assert data["status"] == "success"
    assert "updated" in data["message"]
    
    # Verify file was updated
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == updated_content
    
    # Clean up project
    client.delete(f"/projects/{project_name}")

def test_error_handling(client: TestClient) -> None:
    """Test error handling."""
    
    # Test non-existent project
    response = client.get("/projects/non_existent_project")
    assert response.status_code == 404
    
    # Test non-existent file
    client.post("/projects", json={"name": "error_test_project"})
    response = client.get("/projects/error_test_project/files/non_existent_file")
    assert response.status_code == 404
    
    # Test invalid A2A action
    response = client.post("/a2a", json={
        "action": "invalid_action",
        "parameters": {}
    })
    assert response.status_code == 400
    
    # Test missing required parameters in A2A request
    response = client.post("/a2a", json={
        "action": "memory_bank_read",
        "parameters": {"projectName": "error_test_project"}
    })
    assert response.status_code == 400
    
    # Clean up
    client.delete("/projects/error_test_project")

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 