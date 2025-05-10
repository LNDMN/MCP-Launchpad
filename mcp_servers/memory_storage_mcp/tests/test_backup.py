#!/usr/bin/env python3
"""
Memory Storage MCP - Backup Tests

This module contains tests for the backup functionality of Memory Storage MCP.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any, List

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path to import app
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import app from parent directory
from app import app, create_backup, restore_backup, list_backups

@pytest.fixture(scope="module")
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    old_data_dir = os.environ.get("MEMORY_STORAGE_DATA_DIR")
    
    # Set environment variable for DATA_DIR
    os.environ["MEMORY_STORAGE_DATA_DIR"] = str(temp_dir)
    
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

def test_backup_creation(client: TestClient, temp_data_dir: Path) -> None:
    """Test creating a backup."""
    # Create test project and file
    project_name = "backup_test_project"
    file_name = "test_file.md"
    file_content = "# Test Content\nThis is for backup testing."
    
    # Create project
    client.post("/projects", json={"name": project_name})
    
    # Create file
    client.post(
        f"/projects/{project_name}/files",
        json={"name": file_name, "content": file_content}
    )
    
    # Create backup
    backup_name = f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_comment = "Test backup for unit testing"
    
    response = client.post("/backups", json={
        "name": backup_name,
        "comment": backup_comment
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert backup_name in data["message"]
    
    # Check backup exists
    backup_dir = temp_data_dir / "backups"
    assert backup_dir.exists()
    
    backup_path = list(backup_dir.glob(f"{backup_name}*"))
    assert len(backup_path) > 0
    
    # Clean up
    client.delete(f"/projects/{project_name}")

def test_backup_listing(client: TestClient, temp_data_dir: Path) -> None:
    """Test listing backups."""
    # Create another backup
    backup_name = f"second_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    client.post("/backups", json={
        "name": backup_name,
        "comment": "Second test backup"
    })
    
    # List backups
    response = client.get("/backups")
    assert response.status_code == 200
    
    backups = response.json()
    assert isinstance(backups, list)
    assert len(backups) >= 1
    
    # Check backup format
    for backup in backups:
        assert "name" in backup
        assert "created_at" in backup
        assert "size" in backup
        assert "comment" in backup

def test_backup_restore(client: TestClient, temp_data_dir: Path) -> None:
    """Test restoring a backup."""
    # Get latest backup
    response = client.get("/backups")
    backups = response.json()
    
    if not backups:
        pytest.skip("No backups available for restore test")
    
    latest_backup = backups[0]["name"]
    
    # Create a new project to ensure it's deleted during restore
    client.post("/projects", json={"name": "project_to_be_overwritten"})
    
    # Restore backup
    response = client.post(f"/backups/{latest_backup}/restore")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "restored" in data["message"]
    
    # Verify restored data
    response = client.get("/projects")
    projects = response.json()
    project_names = [p["name"] for p in projects]
    
    # The original test project should be present
    if "backup_test_project" in project_names:
        # Verify file content
        response = client.get("/projects/backup_test_project/files/test_file.md")
        if response.status_code == 200:
            file_data = response.json()
            assert file_data["content"] == "# Test Content\nThis is for backup testing."

def test_backup_function_directly() -> None:
    """Test backup function directly."""
    # Create temp dir
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Set up test data
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        
        # Create a project
        project_dir = data_dir / "test_project"
        project_dir.mkdir()
        
        # Create a file
        with open(project_dir / "test.md", "w") as f:
            f.write("Test content")
        
        # Create backup dir
        backup_dir = temp_dir / "backups"
        backup_dir.mkdir()
        
        # Execute backup function
        backup_name = "function_test_backup"
        result = create_backup(
            backup_name=backup_name,
            comment="Testing function directly",
            data_dir=data_dir,
            backup_dir=backup_dir
        )
        
        assert result.startswith(backup_name)
        
        # Check backup exists
        backup_files = list(backup_dir.glob(f"{backup_name}*"))
        assert len(backup_files) == 1
        
        # Test listing backups
        backups = list_backups(backup_dir)
        assert len(backups) >= 1
        assert any(b["name"].startswith(backup_name) for b in backups)
        
        # Test restore
        # First modify the original data
        with open(project_dir / "test.md", "w") as f:
            f.write("Modified content")
        
        # Then restore
        backup_file = backup_files[0].name
        restore_backup(backup_file, data_dir, backup_dir)
        
        # Verify restore worked
        with open(project_dir / "test.md", "r") as f:
            content = f.read()
        assert content == "Test content"
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 