# Tests for MCP Server

This directory contains tests for the `[SERVER_NAME]` MCP server.

## Tests Overview

- `test_api.py` - API and endpoint tests
- `test_config.py` - configuration tests
- `test_models.py` - data model tests
- `test_utils.py` - utility and helper function tests
- `test_docker_integration.py` - Docker integration tests

## Running Tests

### Local Execution

To run all tests:

```bash
cd mcp_servers/[SERVER_NAME]
python -m pytest tests/
```

For running with code coverage:

```bash
python -m pytest tests/ --cov=. --cov-report=html
```

To run a specific test:

```bash
python -m pytest tests/test_api.py
```

### Docker Integration Tests

To run Docker integration tests, first build the Docker image:

```bash
cd mcp_servers/[SERVER_NAME]
docker build -t [SERVER_NAME]:latest .
```

Then run the tests:

```bash
python -m pytest tests/test_docker_integration.py
```

## Requirements

The following libraries are required to run the tests:

- pytest
- pytest-cov
- fastapi (for API tests)
- httpx (for API tests)
- docker (for Docker integration tests)

You can install dependencies with:

```bash
pip install -r requirements-dev.txt
```

## Test Structure

Tests follow the standard pytest structure:

1. Fixtures for setting up the test environment
2. Test functions with clear names
3. Parameterized tests for checking various scenarios

## Tips for Writing New Tests

- Follow the AAA pattern (Arrange-Act-Assert)
- One test should verify one specific functionality
- Use mocks for external dependencies
- Test both successful scenarios and error handling 