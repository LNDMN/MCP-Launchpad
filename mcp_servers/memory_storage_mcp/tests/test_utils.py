#!/usr/bin/env python3
"""
Memory Storage MCP - Utility Tests

This module tests utility functions of the Memory Storage MCP.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Add parent directory to path to import utility functions
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import utility functions
from app import (
    sanitize_name,
    get_project_path,
    get_file_path,
    validate_project_exists,
    validate_file_exists,
    ensure_directory_exists
)

@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_sanitize_name() -> None:
    """Test name sanitization."""
    # Valid names should remain unchanged
    assert sanitize_name("valid_name") == "valid_name"
    assert sanitize_name("project-123") == "project-123"
    assert sanitize_name("file.md") == "file.md"
    
    # Invalid names should raise ValueError
    with pytest.raises(ValueError):
        sanitize_name("")
    
    with pytest.raises(ValueError):
        sanitize_name("../path_traversal")
    
    with pytest.raises(ValueError):
        sanitize_name("invalid/path")
    
    with pytest.raises(ValueError):
        sanitize_name("name_with\\backslash")
    
    with pytest.raises(ValueError):
        sanitize_name("a" * 101)  # Too long
    
    # Test alphanumeric and allow special chars
    assert sanitize_name("valid-name.md") == "valid-name.md"
    assert sanitize_name("valid_name_123") == "valid_name_123"

def test_path_functions(temp_data_dir: Path) -> None:
    """Test path utility functions."""
    # Test get_project_path
    project_name = "test_project"
    project_path = get_project_path(project_name, temp_data_dir)
    assert project_path == temp_data_dir / project_name
    
    # Test get_file_path
    file_name = "test_file.md"
    file_path = get_file_path(project_name, file_name, temp_data_dir)
    assert file_path == temp_data_dir / project_name / file_name
    
    # Test path traversal prevention
    with pytest.raises(ValueError):
        get_project_path("../traversal", temp_data_dir)
    
    with pytest.raises(ValueError):
        get_file_path("test_project", "../traversal.md", temp_data_dir)
    
    # Test ensure_directory_exists
    new_dir_path = temp_data_dir / "new_directory"
    ensure_directory_exists(new_dir_path)
    assert new_dir_path.exists()
    assert new_dir_path.is_dir()
    
    # Test calling it again doesn't raise errors
    ensure_directory_exists(new_dir_path)
    assert new_dir_path.exists()

def test_validation_functions(temp_data_dir: Path) -> None:
    """Test validation utility functions."""
    # Set up a test project and file
    project_name = "validation_test"
    file_name = "validation_file.md"
    
    project_dir = temp_data_dir / project_name
    project_dir.mkdir()
    
    file_path = project_dir / file_name
    with open(file_path, "w") as f:
        f.write("Test content")
    
    # Test validation of existing project
    assert validate_project_exists(project_name, temp_data_dir) is True
    
    # Test validation of non-existent project
    with pytest.raises(FileNotFoundError):
        validate_project_exists("non_existent_project", temp_data_dir)
    
    # Test validation of existing file
    assert validate_file_exists(project_name, file_name, temp_data_dir) is True
    
    # Test validation of non-existent file
    with pytest.raises(FileNotFoundError):
        validate_file_exists(project_name, "non_existent_file.md", temp_data_dir)
    
    # Test validation with non-existent project
    with pytest.raises(FileNotFoundError):
        validate_file_exists("non_existent_project", file_name, temp_data_dir)

def test_path_security() -> None:
    """Test path security to prevent traversal attacks."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create a dummy structure
        (temp_dir / "public").mkdir()
        (temp_dir / "private").mkdir()
        
        with open(temp_dir / "private" / "secret.txt", "w") as f:
            f.write("Top secret information")
        
        # Try to access outside the intended directory
        dangerous_paths = [
            "../private/secret.txt",
            "../../etc/passwd",
            "%2e%2e/private/secret.txt",
            "public/../private/secret.txt",
            "public/../../etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
        ]
        
        for path in dangerous_paths:
            with pytest.raises(ValueError):
                sanitize_name(path)
                
            # Also test the path functions
            with pytest.raises(ValueError):
                get_project_path(path, temp_dir)
            
            with pytest.raises(ValueError):
                get_file_path("public", path, temp_dir)
    
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 