#!/bin/bash

# Run tests script for memory_storage_mcp
# This script is a wrapper for run_tests.py
# It passes all arguments to the Python script

cd "$(dirname "$0")/.." || exit 1
python run_tests.py "$@" 