#!/usr/bin/env python3
"""
Docker Integration Tests for Memory Storage MCP Server

This module contains integration tests for the Memory Storage MCP server running in a Docker container.
It uses pytest and the Docker Python SDK to start a container and test the API endpoints.
"""

import os
import time
import json
import pytest
import requests
import docker
from docker.errors import NotFound
from typing import Dict, Any, Generator

# Configuration
SERVER_NAME = os.getenv("SERVER_NAME", "memory_storage_mcp")
SERVER_IMAGE = os.getenv("SERVER_IMAGE", f"{SERVER_NAME}:latest")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST_PORT = int(os.getenv("SERVER_HOST_PORT", "8000"))
HEALTH_CHECK_ENDPOINT = os.getenv("HEALTH_CHECK_ENDPOINT", "/")
STARTUP_WAIT_TIME = int(os.getenv("STARTUP_WAIT_TIME", "2"))  # seconds

# Test data
TEST_PROJECT = "test_docker_project"
TEST_FILE = "test_file.md"
TEST_CONTENT = "# Test Content\n\nThis is a test file created during Docker integration testing."

# Environment variables to pass to the container
ENV_VARS = {
    "MEMORY_STORAGE_DATA_DIR": "/app/data",
}


@pytest.fixture(scope="module")
def docker_client() -> docker.DockerClient:
    """Create a Docker client."""
    return docker.from_env()


@pytest.fixture(scope="module")
def docker_container(docker_client: docker.DockerClient) -> Generator[docker.models.containers.Container, None, None]:
    """Start a Docker container for testing."""
    # Check if the container is already running
    try:
        container = docker_client.containers.get(f"{SERVER_NAME}_test")
        # If it exists, stop and remove it
        container.stop()
        container.remove()
    except NotFound:
        # Container doesn't exist, which is fine
        pass

    # Create and start a new container
    container = docker_client.containers.run(
        image=SERVER_IMAGE,
        name=f"{SERVER_NAME}_test",
        detach=True,
        ports={f"{SERVER_PORT}/tcp": SERVER_HOST_PORT},
        environment=ENV_VARS,
        remove=True,
    )

    # Wait for the container to start up
    time.sleep(STARTUP_WAIT_TIME)

    # Check if container is running
    container.reload()
    assert container.status == "running", f"Container failed to start. Status: {container.status}"

    # Check if the server is responding
    max_retries = 5
    retry_delay = 1
    for i in range(max_retries):
        try:
            response = requests.get(f"http://localhost:{SERVER_HOST_PORT}{HEALTH_CHECK_ENDPOINT}")
            if response.status_code == 200:
                break
        except requests.RequestException:
            pass
        
        if i < max_retries - 1:
            time.sleep(retry_delay)
    
    yield container

    # Cleanup
    try:
        container.stop()
    except Exception as e:
        print(f"Error stopping container: {e}")


def test_server_is_healthy(docker_container: docker.models.containers.Container) -> None:
    """Test that the server is up and responding to requests."""
    response = requests.get(f"http://localhost:{SERVER_HOST_PORT}{HEALTH_CHECK_ENDPOINT}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["status"] == "Memory Storage MCP is running"


def test_create_project(docker_container: docker.models.containers.Container) -> None:
    """Test creating a project."""
    response = requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/projects",
        json={"name": TEST_PROJECT}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert TEST_PROJECT in data["message"]


def test_list_projects(docker_container: docker.models.containers.Container) -> None:
    """Test listing projects."""
    response = requests.get(f"http://localhost:{SERVER_HOST_PORT}/projects")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    
    # The test project should be in the list
    project_names = [p["name"] for p in projects]
    assert TEST_PROJECT in project_names


def test_create_file(docker_container: docker.models.containers.Container) -> None:
    """Test creating a file."""
    response = requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{TEST_PROJECT}/files",
        json={"name": TEST_FILE, "content": TEST_CONTENT}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert TEST_FILE in data["message"]


def test_read_file(docker_container: docker.models.containers.Container) -> None:
    """Test reading a file."""
    response = requests.get(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{TEST_PROJECT}/files/{TEST_FILE}"
    )
    assert response.status_code == 200
    file_data = response.json()
    assert file_data["name"] == TEST_FILE
    assert file_data["content"] == TEST_CONTENT


def test_update_file(docker_container: docker.models.containers.Container) -> None:
    """Test updating a file."""
    updated_content = "# Updated Content\n\nThis file has been updated during Docker integration testing."
    response = requests.put(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{TEST_PROJECT}/files/{TEST_FILE}",
        json={"content": updated_content}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify the file was updated
    response = requests.get(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{TEST_PROJECT}/files/{TEST_FILE}"
    )
    assert response.status_code == 200
    file_data = response.json()
    assert file_data["content"] == updated_content


def test_a2a_endpoint(docker_container: docker.models.containers.Container) -> None:
    """Test the A2A-compatible endpoint."""
    # Create a project through A2A
    a2a_create_project = {
        "action": "create_project",
        "parameters": {"name": "a2a_test_project"}
    }
    
    response = requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/a2a",
        json=a2a_create_project
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Create a file through A2A
    a2a_create_file = {
        "action": "create_file",
        "parameters": {
            "project": "a2a_test_project",
            "name": "a2a_test_file.md",
            "content": "# A2A Test Content"
        }
    }
    
    response = requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/a2a",
        json=a2a_create_file
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Read the file through A2A
    a2a_read_file = {
        "action": "read_file",
        "parameters": {
            "project": "a2a_test_project",
            "name": "a2a_test_file.md"
        }
    }
    
    response = requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/a2a",
        json=a2a_read_file
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["content"] == "# A2A Test Content"


def test_data_persistence(docker_container: docker.models.containers.Container) -> None:
    """Test that data persistence works correctly."""
    # Create a unique project and file
    persistence_project = "persistence_test_project"
    persistence_file = "persistence_test.md"
    persistence_content = "# Persistence Test\n\nThis tests data persistence."
    
    # Create project
    requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/projects",
        json={"name": persistence_project}
    )
    
    # Create file
    requests.post(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{persistence_project}/files",
        json={"name": persistence_file, "content": persistence_content}
    )
    
    # Restart the container
    docker_container.restart()
    time.sleep(STARTUP_WAIT_TIME)
    
    # Check if the data is still there after restart
    response = requests.get(
        f"http://localhost:{SERVER_HOST_PORT}/projects/{persistence_project}/files/{persistence_file}"
    )
    assert response.status_code == 200
    file_data = response.json()
    assert file_data["name"] == persistence_file
    assert file_data["content"] == persistence_content


def test_cleanup(docker_container: docker.models.containers.Container) -> None:
    """Clean up test data."""
    # Delete the test projects
    for project in [TEST_PROJECT, "a2a_test_project", "persistence_test_project"]:
        response = requests.delete(f"http://localhost:{SERVER_HOST_PORT}/projects/{project}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert project in data["message"] 