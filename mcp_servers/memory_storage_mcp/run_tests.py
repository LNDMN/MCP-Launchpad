#!/usr/bin/env python3
"""
Memory Storage MCP - Test Runner

This script runs tests for the Memory Storage MCP with various options.
It replaces the bash scripts with a more portable Python implementation.
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional


# ANSI colors for terminal output
class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str) -> None:
    """Print a message with color."""
    print(f"{color}{message}{Colors.NC}")


def install_dependencies() -> None:
    """Install required test dependencies."""
    print_colored("=== Installing test dependencies ===", Colors.YELLOW)
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            "pytest", "httpx", "pytest-cov", "mypy", "pyyaml",
            "pytest-xdist", "pytest-timeout", "pytest-mock"
        ],
        check=True
    )


def run_mypy(project_root: Path) -> bool:
    """Run type checking with mypy."""
    print_colored("=== Running type checking with mypy ===", Colors.YELLOW)
    mypy_result = subprocess.run(
        [
            "mypy", "--config-file=mypy.ini", 
            "app.py", "tests/"
        ],
        cwd=project_root
    )
    
    if mypy_result.returncode == 0:
        print_colored("Type checking passed", Colors.GREEN)
        return True
    else:
        print_colored("Type checking failed", Colors.RED)
        return False


def run_pytest(
    project_root: Path,
    fail_fast: bool = False,
    parallel: bool = False,
    with_coverage: bool = True
) -> bool:
    """Run pytest with the specified options."""
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    if fail_fast:
        cmd.extend(["-xvs"])
    else:
        cmd.extend(["-v"])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    if with_coverage:
        print_colored("=== Running tests with coverage ===", Colors.YELLOW)
        cmd.extend([
            "--cov=.", 
            "--cov-report=term-missing", 
            "--cov-report=html:coverage_html", 
            "--cov-config=pytest.ini"
        ])
    else:
        print_colored("=== Running tests without coverage ===", Colors.YELLOW)
    
    pytest_result = subprocess.run(cmd, cwd=project_root)
    
    if pytest_result.returncode == 0:
        print_colored("=== Tests completed successfully ===", Colors.GREEN)
        
        if with_coverage:
            try:
                # Try to extract coverage percentage
                with open(project_root / "coverage_html" / "index.html", "r") as f:
                    content = f.read()
                    import re
                    match = re.search(r'<span class="pc_cov">([\d]+%)<\/span>', content)
                    if match:
                        coverage = match.group(1)
                        print_colored(f"Total coverage: {coverage}", Colors.GREEN)
            except Exception:
                pass
                
        return True
    else:
        print_colored("=== Tests failed ===", Colors.RED)
        return False


def run_in_docker(project_root: Path, args: List[str]) -> bool:
    """Run tests in a Docker container."""
    print_colored("=== Building Docker test image ===", Colors.YELLOW)
    
    # Create Dockerfile content
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app
COPY . /app/

RUN pip install pytest httpx pytest-cov mypy pyyaml pytest-xdist pytest-timeout pytest-mock

CMD ["python", "run_tests.py"]
"""
    
    # Create temporary Dockerfile
    dockerfile_path = project_root / "Dockerfile.tests"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    try:
        # Build Docker image
        build_result = subprocess.run(
            ["docker", "build", "-t", "memory-storage-mcp-tests", "-f", "Dockerfile.tests", "."],
            cwd=project_root
        )
        
        if build_result.returncode != 0:
            print_colored("Failed to build Docker image", Colors.RED)
            return False
        
        # Run tests in Docker container
        print_colored("=== Running tests in Docker container ===", Colors.YELLOW)
        
        # Convert args to Docker CMD arguments
        docker_cmd = ["python", "run_tests.py"] + args
        
        docker_run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{project_root}:/app",
            "memory-storage-mcp-tests"
        ] + docker_cmd
        
        docker_result = subprocess.run(docker_run_cmd)
        
        if docker_result.returncode == 0:
            print_colored("=== Tests completed successfully in Docker ===", Colors.GREEN)
            return True
        else:
            print_colored("=== Tests failed in Docker ===", Colors.RED)
            return False
    
    finally:
        # Clean up temporary Dockerfile
        if dockerfile_path.exists():
            os.unlink(dockerfile_path)


def open_coverage_report(project_root: Path) -> None:
    """Open coverage report in browser."""
    report_path = project_root / "coverage_html" / "index.html"
    
    if not report_path.exists():
        print_colored("Coverage report not found", Colors.YELLOW)
        return
    
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", report_path])
        elif sys.platform == "win32":  # Windows
            os.startfile(report_path)
        else:  # Linux
            subprocess.run(["xdg-open", report_path])
    except Exception as e:
        print(f"Could not open browser: {e}")


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for Memory Storage MCP")
    parser.add_argument("--skip-mypy", action="store_true", help="Skip mypy type checking")
    parser.add_argument("--skip-coverage", action="store_true", help="Skip coverage analysis")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--fail-fast", "-f", action="store_true", help="Stop on first failure")
    parser.add_argument("--docker", "-d", action="store_true", help="Run tests in Docker")
    parser.add_argument("--view-coverage", "-v", action="store_true", help="Open coverage report in browser")
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    if args.docker:
        # Remove --docker from args to prevent infinite recursion
        docker_args = [arg for arg in sys.argv[1:] if arg not in ["--docker", "-d"]]
        return 0 if run_in_docker(project_root, docker_args) else 1
    
    # Install dependencies
    try:
        install_dependencies()
    except subprocess.CalledProcessError:
        print_colored("Failed to install dependencies", Colors.RED)
        return 1
    
    # Run type checking
    if not args.skip_mypy:
        if not run_mypy(project_root):
            return 1
    else:
        print_colored("Skipping mypy type checking", Colors.YELLOW)
    
    # Run tests
    test_success = run_pytest(
        project_root,
        fail_fast=args.fail_fast,
        parallel=args.parallel,
        with_coverage=not args.skip_coverage
    )
    
    # Open coverage report if requested
    if args.view_coverage and not args.skip_coverage and test_success:
        open_coverage_report(project_root)
    
    return 0 if test_success else 1


if __name__ == "__main__":
    sys.exit(main()) 