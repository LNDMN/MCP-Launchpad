#!/usr/bin/env python3
"""
Memory Storage MCP - CI Test Runner

This script runs tests for Memory Storage MCP in CI/CD environments.
It includes additional options for CI-specific functionality like JUnit XML reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple


def run_in_ci(
    project_root: Path,
    junit: bool = True,
    coverage_xml: bool = True,
    fail_fast: bool = False,
) -> Tuple[bool, Optional[float]]:
    """
    Run tests in CI environment.
    
    Args:
        project_root: Path to the project root
        junit: Whether to generate JUnit XML report
        coverage_xml: Whether to generate coverage XML report
        fail_fast: Whether to stop on first failure
        
    Returns:
        Tuple of (success: bool, coverage_percentage: Optional[float])
    """
    # Print environment information
    print(f"Python version: {sys.version}")
    print(f"Running in directory: {project_root}")
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "--quiet",
            "pytest", "httpx", "pytest-cov", "mypy", "pyyaml"
        ],
        check=True
    )
    
    # Run mypy
    print("Running type checking...")
    mypy_result = subprocess.run(
        ["mypy", "--config-file=mypy.ini", "app.py", "tests/"],
        cwd=project_root
    )
    
    if mypy_result.returncode != 0:
        print("Type checking failed!")
        return False, None
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    if fail_fast:
        cmd.append("-xvs")
    
    # Add coverage options
    cmd.extend(["--cov=.", "--cov-report=term"])
    
    if coverage_xml:
        cmd.append("--cov-report=xml:coverage.xml")
    
    if junit:
        cmd.append("--junitxml=junit.xml")
    
    # Run tests
    print("Running tests...")
    test_result = subprocess.run(cmd, cwd=project_root)
    
    # Get coverage percentage if available
    coverage_percentage = None
    if test_result.returncode == 0 and coverage_xml:
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(project_root / "coverage.xml")
            root = tree.getroot()
            coverage_percentage = float(root.attrib.get("line-rate", "0")) * 100
            print(f"Coverage: {coverage_percentage:.2f}%")
        except Exception as e:
            print(f"Error parsing coverage data: {e}")
    
    success = test_result.returncode == 0
    if success:
        print("Tests passed successfully!")
    else:
        print("Tests failed!")
    
    return success, coverage_percentage


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for Memory Storage MCP in CI")
    parser.add_argument("--no-junit", action="store_true", help="Disable JUnit XML report")
    parser.add_argument("--no-coverage-xml", action="store_true", help="Disable coverage XML report")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--min-coverage", type=float, default=80.0, help="Minimum coverage percentage required")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Run tests
    success, coverage = run_in_ci(
        project_root,
        junit=not args.no_junit,
        coverage_xml=not args.no_coverage_xml,
        fail_fast=args.fail_fast
    )
    
    # Check minimum coverage
    if success and coverage is not None and coverage < args.min_coverage:
        print(f"Coverage ({coverage:.2f}%) is below minimum required ({args.min_coverage}%)")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 