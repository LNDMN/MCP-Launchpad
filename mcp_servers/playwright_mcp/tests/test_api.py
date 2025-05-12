import pytest
from fastapi.testclient import TestClient # Keep TestClient import if needed locally
import subprocess
import time
import json
import os

# Import the client fixture from conftest
from .conftest import client

# --- Local FastAPI App Tests (using TestClient) ---

def test_health_check(client: TestClient):
    """Test the /health endpoint directly using TestClient."""
    if client is None:
        pytest.skip("TestClient not available, likely app import failed.")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_mcp_tools_list_local(client: TestClient):
    """Test the MCP tools/list method directly using TestClient."""
    if client is None:
        pytest.skip("TestClient not available, likely app import failed.")
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "test_list_local"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("jsonrpc") == "2.0"
    assert data.get("id") == "test_list_local"
    assert "result" in data
    assert "tools" in data["result"]
    assert isinstance(data["result"]["tools"], list)
    # Check for placeholder tools defined in src/main.py
    placeholder_tool_names = [t['name'] for t in data["result"]["tools"]]
    assert "browser_navigate" in placeholder_tool_names
    assert "browser_click" in placeholder_tool_names

# --- Docker Container Integration Tests ---

# Get the path to the playwright_mcp directory relative to the test file
PLAYWRIGHT_MCP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_NAME = "mcp_launchpad/playwright_mcp:latest"
CONTAINER_NAME = "playwright_mcp_test_container"
TEST_PORT = 8000 # Match the port exposed in the updated Dockerfile
MCP_ENDPOINT_PATH = "/" # Assuming the MCP endpoint is at the root

@pytest.fixture(scope="module", autouse=True)
def build_docker_image():
    """Builds the Docker image before running tests in this module."""
    print(f"\nBuilding Docker image: {IMAGE_NAME} from {PLAYWRIGHT_MCP_DIR}")
    try:
        # Use DOCKER_BUILDKIT=1 for potentially faster builds
        build_env = os.environ.copy()
        build_env["DOCKER_BUILDKIT"] = "1"
        subprocess.run(
            ["docker", "build", "-t", IMAGE_NAME, "."],
            cwd=PLAYWRIGHT_MCP_DIR,
            check=True,
            capture_output=True, # Capture output to check for errors
            text=True,
            env=build_env
        )
        print(f"Docker image {IMAGE_NAME} built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Docker build failed. Error: {e.stderr}")
        pytest.fail(f"Docker build failed: {e.stderr}", pytrace=False)
    except FileNotFoundError:
        pytest.fail("Docker command not found. Is Docker installed and in PATH?", pytrace=False)

@pytest.fixture(scope="module")
def playwright_mcp_server_docker():
    """Fixture to run and clean up the playwright_mcp Docker container."""
    container_id = None
    try:
        print(f"\nStarting Docker container {CONTAINER_NAME} from image {IMAGE_NAME}...")
        run_command = [
            "docker", "run", "-d", "--rm",
            "-p", f"{TEST_PORT}:{TEST_PORT}", # Map host port to container port
            "--name", CONTAINER_NAME,
            IMAGE_NAME
        ]
        process = subprocess.run(run_command, check=True, capture_output=True, text=True)
        container_id = process.stdout.strip()
        print(f"Container {CONTAINER_NAME} started with ID: {container_id}")

        # Increased wait time for Playwright initialization within the container
        wait_time = 15
        print(f"Waiting {wait_time} seconds for container to initialize...")
        time.sleep(wait_time)

        # Check container health/logs
        logs_process = subprocess.run(["docker", "logs", CONTAINER_NAME], capture_output=True, text=True, timeout=10)
        print(f"--- Container Logs ({CONTAINER_NAME}) ---")
        print(logs_process.stdout)
        print(logs_process.stderr)
        print("--- End Container Logs ---")

        # Basic check for common startup errors
        if "error" in logs_process.stderr.lower() or "traceback" in logs_process.stderr.lower():
             # Ignore known benign Playwright/uvicorn errors if necessary
             if "address already in use" not in logs_process.stderr: # Example ignore
                 print(f"Potential startup error detected in container logs.")
                 # Optionally fail the test setup here
                 # pytest.fail(...) 

        # Check connectivity
        server_url = f"http://localhost:{TEST_PORT}/health" # Use health endpoint
        retries = 3
        connected = False
        for i in range(retries):
             try:
                 curl_check = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", server_url], capture_output=True, text=True, timeout=5)
                 if curl_check.stdout.strip() == "200":
                     print("Container health check successful.")
                     connected = True
                     break
                 else:
                     print(f"Health check attempt {i+1} failed with code: {curl_check.stdout.strip()}. Retrying...")
             except Exception as e:
                 print(f"Health check attempt {i+1} failed with exception: {e}. Retrying...")
             time.sleep(3)
        
        if not connected:
             pytest.fail(f"Failed to connect to the container at {server_url} after {retries} retries.")

        yield f"http://localhost:{TEST_PORT}{MCP_ENDPOINT_PATH}"

    finally:
        if container_id:
            print(f"\nStopping container {CONTAINER_NAME} ({container_id})...")
            subprocess.run(["docker", "stop", container_id], check=False, capture_output=True)
            print(f"Container {CONTAINER_NAME} stopped.")
        else:
            # Attempt cleanup by name if ID wasn't captured but container might exist
            subprocess.run(["docker", "stop", CONTAINER_NAME], check=False, capture_output=True)
            subprocess.run(["docker", "rm", CONTAINER_NAME], check=False, capture_output=True)

def test_server_starts_successfully_docker(playwright_mcp_server_docker):
    """Test verifies the Docker container starts successfully."""
    server_url = playwright_mcp_server_docker # This fixture handles startup checks
    assert server_url is not None
    print(f"Docker container test: Server seems to be running at {server_url}")

def test_list_tools_docker(playwright_mcp_server_docker):
    """Test tools/list via the running Docker container."""
    server_url = playwright_mcp_server_docker
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "test_list_docker"
    }

    curl_command = [
        "curl", "-s",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(mcp_request),
        server_url
    ]

    print(f"\nExecuting curl: {' '.join(curl_command)}")
    try:
        process = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=False, # Don't fail immediately on non-zero exit code
            timeout=15
        )

        print(f"Curl stdout: {process.stdout}")
        print(f"Curl stderr: {process.stderr}")

        if process.returncode != 0:
            # Check for connection refused specifically
            if "Connection refused" in process.stderr or "Failed to connect" in process.stderr:
                 pytest.fail(f"Curl command failed with connection error: {process.stderr}")
            # Log other curl errors but don't necessarily fail if stdout has content
            print(f"Warning: Curl command exited with code {process.returncode}. Stderr: {process.stderr}")

        # Try to parse JSON even if curl had non-zero exit (e.g., HTTP 500)
        response_data = json.loads(process.stdout)

        assert response_data.get("jsonrpc") == "2.0", f"Invalid JSON-RPC version: {response_data.get('jsonrpc')}"
        assert response_data.get("id") == "test_list_docker", f"Mismatched ID: {response_data.get('id')}"

        # Check for JSON-RPC level error first
        if "error" in response_data:
            pytest.fail(f"MCP server returned an error: {response_data['error']}")

        assert "result" in response_data, f"'result' field missing: {response_data}"
        result_content = response_data["result"]
        assert "tools" in result_content, f"'tools' field missing in result: {result_content}"
        tools_list = result_content["tools"]
        assert isinstance(tools_list, list), "'tools' should be a list"
        assert len(tools_list) > 0, "Tools list should not be empty (even placeholders)"

        # Check for placeholder tools from src/main.py
        actual_tool_names = [tool.get("name") for tool in tools_list]
        print(f"Actual tool names from container: {actual_tool_names}")
        expected_tools = ["browser_navigate", "browser_click", "browser_type", "browser_snapshot"]
        for tool_name in expected_tools:
            assert tool_name in actual_tool_names, f"Expected placeholder tool '{tool_name}' not found in {actual_tool_names}"

    except subprocess.TimeoutExpired:
        pytest.fail("Curl command timed out after 15 seconds.")
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON response: {e}. Response body: '{process.stdout if process else 'No stdout'}'")
    except KeyError as e:
        pytest.fail(f"Key error in JSON response: {e}. Response data: {response_data if 'response_data' in locals() else 'N/A'}")


# Removed old placeholder test
# def test_dummy_endpoint(client):
#     assert True

# Keep other Docker tests as placeholders
# def test_navigate_and_snapshot_docker(playwright_mcp_server_docker):
#     pass

# def test_type_and_verify_docker(playwright_mcp_server_docker):
#     pass

# TODO: Добавить тесты для вызова конкретных инструментов:
# - test_navigate_and_snapshot
# - test_type_and_verify
# - и т.д.

# TODO: Добавить тесты для основных функций Playwright MCP:
# - test_navigate_to_url
# - test_get_page_content
# - test_click_element
# - test_type_into_element
# - test_browser_snapshot
# - и т.д.
# Эти тесты потребуют отправки конкретных MCP команд и проверки результатов.

# Пример заглушки для теста навигации
# def test_navigate_to_url(playwright_mcp_server):
#     server_url = playwright_mcp_server
#     # Сформировать MCP запрос для browser_navigate
#     # Отправить запрос (например, через curl или Python HTTP клиент, если возможно)
#     # Проверить ответ и, возможно, состояние браузера (через другой MCP запрос, например, browser_snapshot)
#     pass

# TODO: Добавить тесты для проверки запуска в Docker 

# Placeholder test - replace with actual API tests
def test_dummy_endpoint(client):
    # Example using the client fixture from conftest.py
    # Replace with actual endpoint and expected response
    # response = client.get("/api/v1/status")
    # assert response.status_code == 200
    # assert response.json() == {"status": "ok"}
    assert True # Placeholder assertion

# Add more tests for different API endpoints and functionalities 