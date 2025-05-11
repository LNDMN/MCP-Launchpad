#!/usr/bin/env python3
"""
Common pytest fixtures for MCP server tests.

This module contains common fixtures that can be used across tests.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Any, Dict

import pytest

# Uncomment if using FastAPI
# from fastapi.testclient import TestClient
# from app import app


@pytest.fixture(scope="function")
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def temp_file() -> Generator[Path, None, None]:
    """Create a temporary file for tests."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    file_path = Path(path)
    yield file_path
    file_path.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def test_data() -> Dict[str, Any]:
    """Return test data that can be used across tests."""
    return {
        "project_name": "test_project",
        "file_name": "test_file.md",
        "content": "# Test Content\n\nThis is a test file.",
        "metadata": {
            "key1": "value1",
            "key2": "value2",
            "nested": {
                "key3": "value3"
            }
        }
    }


# Uncomment if using FastAPI
# @pytest.fixture(scope="module")
# def client() -> Generator[TestClient, None, None]:
#     """Return a FastAPI TestClient instance."""
#     with TestClient(app) as client:
#         yield client


# Uncomment if using custom environment variables for testing
# @pytest.fixture(scope="function")
# def env_vars() -> Generator[None, None, None]:
#     """Set up environment variables for testing."""
#     original_env = os.environ.copy()
#     os.environ["TEST_VAR_1"] = "test_value_1"
#     os.environ["TEST_VAR_2"] = "test_value_2"
#     
#     yield
#     
#     # Restore the original environment variables
#     os.environ.clear()
#     os.environ.update(original_env)


# Add more common fixtures that make sense for your MCP server
# @pytest.fixture(scope="function")
# def your_custom_fixture() -> Any:
#     """Description of your custom fixture."""
#     # Setup code
#     data = ...
#     yield data
#     # Teardown code 