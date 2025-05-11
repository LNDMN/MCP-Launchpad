# Memory Storage MCP Tests

This directory contains the test suite for the Memory Storage MCP server.

## Test Structure

The tests are organized by functionality:

- `test_api.py`: Tests for the REST API endpoints
- `test_backup.py`: Tests for backup and restore functionality
- `test_config.py`: Tests for configuration loading and management
- `test_models.py`: Tests for data models and validation
- `test_utils.py`: Tests for utility functions
- `test_docker_integration.py`: Docker integration tests

## Running Tests

You can run tests using the provided Python scripts or shell wrappers:

### Local Testing

To run tests locally:

```bash
# Run all tests with coverage
python ../run_tests.py

# Or use the shell script
../scripts/run_tests.sh

# Skip type checking
../scripts/run_tests.sh --skip-mypy

# Skip coverage analysis
../scripts/run_tests.sh --skip-coverage

# Run tests in parallel
../scripts/run_tests.sh --parallel

# Stop on first failure
../scripts/run_tests.sh --fail-fast

# Open coverage report in browser after tests complete
../scripts/run_tests.sh --view-coverage
```

### Docker Integration Testing

For testing the Docker container:

```bash
# Build the Docker image
cd ..
docker build -t memory_storage_mcp:latest .

# Run Docker integration tests
python -m pytest tests/test_docker_integration.py -v
```

### Docker Testing

For isolated testing in Docker:

```bash
# Run all tests in Docker
python ../run_tests.py --docker

# Or use the dedicated Docker test script
../scripts/docker_tests.sh

# Pass additional arguments
../scripts/docker_tests.sh --skip-mypy --parallel
```

### CI/CD Testing

For continuous integration environments:

```bash
# Run tests with default options (JUnit XML and coverage XML reports)
python ../ci_tests.py

# Set minimum coverage requirement
python ../ci_tests.py --min-coverage 90

# Disable JUnit XML report
python ../ci_tests.py --no-junit

# Disable coverage XML report
python ../ci_tests.py --no-coverage-xml
```

## Test Data Management

You can manage test data using the provided script:

```bash
# Set up test environment
python ../manage_test_data.py setup --data-dir ./test_data

# Generate test data
python ../manage_test_data.py generate --projects 5 --files 10

# Create a backup of test data
python ../manage_test_data.py backup --name test_backup --comment "Test backup"

# Clean up test environment
python ../manage_test_data.py clean
```

## Test Coverage

The test suite includes:

- **API Tests**: Validates all REST endpoints and their functionality
- **Backup Tests**: Verifies backup creation, listing, and restoration
- **Configuration Tests**: Checks config loading from files and environment variables
- **Model Tests**: Ensures data validation works correctly
- **Utility Tests**: Validates helper functions and security measures
- **Docker Integration Tests**: Verifies functionality in a Docker container

## Type Checking

The project uses `mypy` for static type checking. All code and tests are type-checked to ensure type safety.

## Test Dependencies

All dependencies are listed in the `requirements-dev.txt` file in the server's root directory:

```bash
pip install -r ../requirements-dev.txt
```

Key dependencies include:
- pytest
- pytest-cov
- httpx
- docker
- requests
- mypy
- pyyaml
- pytest-xdist (for parallel testing)
- pytest-timeout
- pytest-mock 