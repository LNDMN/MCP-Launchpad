#!/bin/bash

# Docker tests script for memory_storage_mcp
# Runs tests inside a Docker container

cd "$(dirname "$0")/.." || exit 1

echo "=== Building Docker test image using docker-compose ==="
docker-compose build || exit 1

echo "=== Running tests in Docker container ==="
docker-compose run --rm \
  memory-storage-mcp \
  python run_tests.py "$@"

exit_code=$?
echo "=== Tests completed with exit code: $exit_code ==="

exit $exit_code 