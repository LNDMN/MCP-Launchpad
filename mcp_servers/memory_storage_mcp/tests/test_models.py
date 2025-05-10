#!/usr/bin/env python3
"""
Memory Storage MCP - Model Tests

This module contains tests for the Pydantic models used in Memory Storage MCP.
"""

import pytest
from pydantic import ValidationError
from typing import Dict, Any, List

# Add parent directory to path to import models
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Import models from app
from app import ProjectModel, FileModel, BackupModel, A2ARequest

def test_project_model() -> None:
    """Test ProjectModel validation."""
    # Valid case
    project = ProjectModel(name="valid_project")
    assert project.name == "valid_project"
    
    # Invalid cases
    with pytest.raises(ValidationError):
        ProjectModel(name="")  # Empty name
    
    with pytest.raises(ValidationError):
        ProjectModel(name="invalid/project")  # Contains slash
    
    with pytest.raises(ValidationError):
        ProjectModel(name="a" * 101)  # Too long
    
    # Test model dict output
    assert project.dict() == {"name": "valid_project"}

def test_file_model() -> None:
    """Test FileModel validation."""
    # Valid case
    file = FileModel(name="test.md", content="# Test")
    assert file.name == "test.md"
    assert file.content == "# Test"
    
    # Invalid cases
    with pytest.raises(ValidationError):
        FileModel(name="", content="test")  # Empty name
    
    with pytest.raises(ValidationError):
        FileModel(name="invalid/file.md", content="test")  # Contains slash
    
    with pytest.raises(ValidationError):
        FileModel(name="a" * 101 + ".md", content="test")  # Too long
    
    # Test model dict output
    assert file.dict() == {"name": "test.md", "content": "# Test"}

def test_backup_model() -> None:
    """Test BackupModel validation."""
    # Valid case
    backup = BackupModel(name="test_backup", comment="Test comment")
    assert backup.name == "test_backup"
    assert backup.comment == "Test comment"
    
    # Valid case with minimal fields
    backup_minimal = BackupModel(name="minimal_backup")
    assert backup_minimal.name == "minimal_backup"
    assert backup_minimal.comment == ""
    
    # Invalid cases
    with pytest.raises(ValidationError):
        BackupModel(name="")  # Empty name
    
    with pytest.raises(ValidationError):
        BackupModel(name="invalid/backup")  # Contains slash
    
    with pytest.raises(ValidationError):
        BackupModel(name="a" * 101)  # Too long
    
    # Test model dict output
    assert backup.dict() == {"name": "test_backup", "comment": "Test comment"}
    assert backup_minimal.dict() == {"name": "minimal_backup", "comment": ""}

def test_a2a_request_model() -> None:
    """Test A2ARequest validation."""
    # Valid cases
    list_projects = A2ARequest(action="list_projects", parameters={})
    assert list_projects.action == "list_projects"
    assert list_projects.parameters == {}
    
    read_file = A2ARequest(
        action="memory_bank_read",
        parameters={"projectName": "test", "fileName": "test.md"}
    )
    assert read_file.action == "memory_bank_read"
    assert read_file.parameters == {"projectName": "test", "fileName": "test.md"}
    
    # Invalid cases
    with pytest.raises(ValidationError):
        A2ARequest(action="invalid_action", parameters={})  # Invalid action
    
    with pytest.raises(ValidationError):
        A2ARequest(action="memory_bank_read", parameters={})  # Missing required parameters
    
    # Test different actions
    valid_actions = [
        ("list_projects", {}),
        ("list_project_files", {"projectName": "test"}),
        ("memory_bank_read", {"projectName": "test", "fileName": "test.md"}),
        ("memory_bank_write", {"projectName": "test", "fileName": "test.md", "content": "data"}),
        ("memory_bank_update", {"projectName": "test", "fileName": "test.md", "content": "data"})
    ]
    
    for action, params in valid_actions:
        valid_req = A2ARequest(action=action, parameters=params)
        assert valid_req.action == action
        assert valid_req.parameters == params

def test_parameter_validation() -> None:
    """Test parameter validation in A2ARequest."""
    # Missing projectName
    with pytest.raises(ValidationError):
        A2ARequest(
            action="list_project_files",
            parameters={}
        )
    
    # Missing fileName
    with pytest.raises(ValidationError):
        A2ARequest(
            action="memory_bank_read",
            parameters={"projectName": "test"}
        )
    
    # Missing content
    with pytest.raises(ValidationError):
        A2ARequest(
            action="memory_bank_write",
            parameters={"projectName": "test", "fileName": "test.md"}
        )
    
    # Invalid project name
    with pytest.raises(ValidationError):
        A2ARequest(
            action="memory_bank_read",
            parameters={"projectName": "invalid/project", "fileName": "test.md"}
        )
    
    # Invalid file name
    with pytest.raises(ValidationError):
        A2ARequest(
            action="memory_bank_read",
            parameters={"projectName": "test", "fileName": "invalid/file.md"}
        )

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 