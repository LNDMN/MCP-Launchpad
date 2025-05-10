# Memory Storage MCP Tests

This directory contains the test suite for the Memory Storage MCP server.

## Test Structure

The tests are organized by functionality:

- `test_api.py`: Tests for the REST API endpoints
- `test_backup.py`: Tests for backup and restore functionality
- `test_config.py`: Tests for configuration loading and management
- `test_models.py`: Tests for data models and validation
- `test_utils.py`: Tests for utility functions

## Running Tests

You can run tests using the provided Python scripts:

### Local Testing

To run tests locally:

```bash
# Run all tests with coverage
./run_tests.py

# Skip type checking
./run_tests.py --skip-mypy

# Skip coverage analysis
./run_tests.py --skip-coverage

# Run tests in parallel
./run_tests.py --parallel

# Stop on first failure
./run_tests.py --fail-fast

# Open coverage report in browser after tests complete
./run_tests.py --view-coverage
```

### Docker Testing

For isolated testing in Docker:

```bash
# Run all tests in Docker
./run_tests.py --docker

# Pass additional arguments
./run_tests.py --docker --skip-mypy --parallel
```

### CI/CD Testing

For continuous integration environments:

```bash
# Run tests with default options (JUnit XML and coverage XML reports)
./ci_tests.py

# Set minimum coverage requirement
./ci_tests.py --min-coverage 90

# Disable JUnit XML report
./ci_tests.py --no-junit

# Disable coverage XML report
./ci_tests.py --no-coverage-xml
```

## Test Data Management

You can manage test data using the provided script:

```bash
# Set up test environment
./manage_test_data.py setup --data-dir ./test_data

# Generate test data
./manage_test_data.py generate --projects 5 --files 10

# Create a backup of test data
./manage_test_data.py backup --name test_backup --comment "Test backup"

# Clean up test environment
./manage_test_data.py clean
```

## Test Coverage

The test suite includes:

- **API Tests**: Validates all REST endpoints and their functionality
- **Backup Tests**: Verifies backup creation, listing, and restoration
- **Configuration Tests**: Checks config loading from files and environment variables
- **Model Tests**: Ensures data validation works correctly
- **Utility Tests**: Validates helper functions and security measures

## Type Checking

The project uses `mypy` for static type checking. All code and tests are type-checked to ensure type safety.

## Test Dependencies

- pytest
- pytest-cov
- httpx
- mypy
- pyyaml
- pytest-xdist (for parallel testing)
- pytest-timeout
- pytest-mock 