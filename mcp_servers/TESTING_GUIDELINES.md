# MCP Server Testing Guidelines

This document contains guidelines and standards for testing MCP servers within the MCP-Launchpad project.

## General Principles

1. **All tests must be written in Python** - we use Python as the standard language for testing all MCP servers.
2. **Use pytest** - the main testing framework for our project.
3. **Isolate tests** - tests should not depend on external resources or other tests.
4. **Automate** - all tests should be automated and run through CI/CD.
5. **Cover all functions** - aim for maximum code coverage with tests.

## Test Structure

For each MCP server, create a `tests` folder with the following recommended structure:

```
mcp_servers/your_server/
├── tests/
│   ├── README.md               # Test description and instructions
│   ├── conftest.py             # Common fixtures and pytest settings
│   ├── test_config.py          # Configuration tests
│   ├── test_api.py             # API and endpoint tests
│   ├── test_models.py          # Data model tests (if applicable)
│   ├── test_utils.py           # Utility function tests
│   ├── test_integration.py     # Integration tests
│   └── data/                   # Test data (if needed)
```

## Using pytest

### Basic Fixtures

```python
import pytest
from fastapi.testclient import TestClient

# For FastAPI servers
@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    from your_server.app import app
    with TestClient(app) as client:
        yield client

# For temporary data
@pytest.fixture(scope="function")
def temp_data_dir():
    """Create a temporary directory for test data."""
    import tempfile
    import shutil
    from pathlib import Path
    
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)
```

### Test Organization

```python
def test_feature_name(client, other_fixtures):
    """Test should have a clear description of what it verifies."""
    # Setup
    test_data = {"key": "value"}
    
    # Action
    response = client.post("/endpoint", json=test_data)
    
    # Verification
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
```

## Testing A2A Compatibility

For MCP servers with A2A (Agent-to-Agent) support, add specific tests:

```python
def test_a2a_endpoint(client):
    """Test the A2A-compatible endpoint."""
    a2a_request = {
        "type": "a2a_request",
        "action": "specific_action",
        "parameters": {"param1": "value1"}
    }
    
    response = client.post("/a2a", json=a2a_request)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Additional A2A response checks
```

## Docker Integration Testing

For testing Docker containers:

```python
import docker
import pytest
import requests
import time

@pytest.fixture(scope="module")
def docker_container():
    """Start a Docker container for testing."""
    client = docker.from_env()
    container = client.containers.run(
        "your-mcp-server:latest",
        detach=True,
        ports={"8000/tcp": 8000},
        environment={"ENV_VAR": "value"}
    )
    
    # Wait for container to start
    time.sleep(2)
    
    yield container
    
    # Cleanup
    container.stop()
    container.remove()

def test_docker_api(docker_container):
    """Test the API through the Docker container."""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    # Additional assertions
```

## Test Writing Guidelines

1. **Use descriptive names** - the test name should clearly describe what it verifies.
2. **Follow the AAA pattern** - Arrange (setup), Act (action), Assert (verification).
3. **One test, one function** - a test should verify one specific functionality.
4. **Use parameterization** - for testing different input variants.
5. **Test edge cases** - not just successful scenarios, but error handling too.
6. **Isolate external dependencies** - use mocks and stubs for external services.

## Running Tests

Tests can be run from the MCP server's root directory:

```bash
cd mcp_servers/your_server
python -m pytest tests/
```

For running with code coverage:

```bash
python -m pytest tests/ --cov=your_server --cov-report=html
```

## CI/CD Integration

All tests should be integrated into the CI/CD pipeline. Examples of GitHub Actions configuration will be provided in the project's common directory. 