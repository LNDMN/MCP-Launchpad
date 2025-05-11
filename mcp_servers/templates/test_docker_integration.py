#!/usr/bin/env python3
"""
Docker Integration Tests for MCP Server

This module contains integration tests for the MCP server running in a Docker container.
It uses pytest and the Docker Python SDK to start a container and test the API.
"""

import os
import time
import pytest
import requests
import docker
from docker.errors import NotFound

# Configuration
SERVER_NAME = os.getenv("SERVER_NAME", "mcp_server")  # Replace with your server name
SERVER_IMAGE = os.getenv("SERVER_IMAGE", f"{SERVER_NAME}:latest")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST_PORT = int(os.getenv("SERVER_HOST_PORT", "8000"))
HEALTH_CHECK_ENDPOINT = os.getenv("HEALTH_CHECK_ENDPOINT", "/")
STARTUP_WAIT_TIME = int(os.getenv("STARTUP_WAIT_TIME", "2"))  # seconds

# Environment variables to pass to the container
ENV_VARS = {
    # Add your environment variables here
    # "ENV_VAR_NAME": "value",
}


@pytest.fixture(scope="module")
def docker_client():
    """Create a Docker client."""
    return docker.from_env()


@pytest.fixture(scope="module")
def docker_container(docker_client):
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


def test_server_is_healthy(docker_container):
    """Test that the server is up and responding to requests."""
    response = requests.get(f"http://localhost:{SERVER_HOST_PORT}{HEALTH_CHECK_ENDPOINT}")
    assert response.status_code == 200
    # You can add more specific assertions about the health check response here


def test_api_endpoint_example(docker_container):
    """Example test for a specific API endpoint."""
    # Replace with your actual endpoint and expected response
    endpoint = "/example"
    payload = {"key": "value"}
    
    # Uncomment and adapt as needed
    # response = requests.post(
    #     f"http://localhost:{SERVER_HOST_PORT}{endpoint}",
    #     json=payload
    # )
    # assert response.status_code == 200
    # data = response.json()
    # assert "status" in data
    # assert data["status"] == "success"


# Add more specific tests for your MCP server endpoints below
# def test_specific_feature(docker_container):
#     ...


# Test A2A compatibility if applicable
def test_a2a_endpoint(docker_container):
    """Test the A2A-compatible endpoint if available."""
    # Uncomment and adapt if your server supports A2A
    # a2a_request = {
    #     "type": "a2a_request",
    #     "action": "specific_action",
    #     "parameters": {"param1": "value1"}
    # }
    # 
    # response = requests.post(
    #     f"http://localhost:{SERVER_HOST_PORT}/a2a",
    #     json=a2a_request
    # )
    # assert response.status_code == 200
    # data = response.json()
    # assert data["status"] == "success"
    # Additional A2A response checks
    pass


# If your server needs to persist data, test that it works correctly
def test_data_persistence(docker_container):
    """Test that data persistence works correctly if applicable."""
    # This is just a placeholder test
    # Implement according to your server's data persistence mechanisms
    pass 