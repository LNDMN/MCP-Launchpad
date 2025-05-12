import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import os

# Import fixtures from conftest
from .conftest import client, temp_fs # temp_fs implicitly used by client fixture setup


# --- Local FastAPI App Tests ---

def test_fs_health_check(client: TestClient):
    """Test the filesystem server's /health endpoint."""
    if client is None: pytest.skip("Client fixture failed")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # Check if READ_ONLY and ALLOWED_PATHS reflect conftest setup
    assert data["read_only"] == False
    assert data["allowed_paths_configured"] == True

def test_fs_tools_list_local(client: TestClient):
    """Test the MCP tools/list method for filesystem tools."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {"jsonrpc": "2.0", "method": "tools/list", "id": "fs_list_local"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("jsonrpc") == "2.0"
    assert data.get("id") == "fs_list_local"
    assert "result" in data
    assert "tools" in data["result"]
    tool_names = [t['name'] for t in data["result"]["tools"]]
    assert "listDirectory" in tool_names
    assert "readFile" in tool_names
    assert "writeFile" in tool_names

# --- Filesystem Operation Tests ---

def test_list_directory_success(client: TestClient, temp_fs: Path):
    """Test listing the root allowed directory."""
    if client is None: pytest.skip("Client fixture failed")
    # Resolve the temp_fs path provided by the fixture to ensure it's absolute
    # The path used in the request MUST match how it's seen inside the test environment / ALLOWED_PATHS
    allowed_test_path = "/test_data"
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "listDirectory", 
        "params": {"path": allowed_test_path}, 
        "id": "list_root"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "list_root"
    assert "result" in data
    # The server should return the resolved path it used
    assert data["result"]["path"] == allowed_test_path 
    entries = {e["name"]: e for e in data["result"]["entries"]}
    assert "file1.txt" in entries
    assert entries["file1.txt"]["type"] == "file"
    assert "subdir1" in entries
    assert entries["subdir1"]["type"] == "directory"

def test_list_directory_subdir(client: TestClient, temp_fs: Path):
    """Test listing a subdirectory."""
    if client is None: pytest.skip("Client fixture failed")
    subdir_path = "/test_data/subdir1"
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "listDirectory", 
        "params": {"path": subdir_path}, 
        "id": "list_subdir"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "list_subdir"
    assert "result" in data
    assert data["result"]["path"] == subdir_path
    entries = {e["name"]: e for e in data["result"]["entries"]}
    assert "file2.txt" in entries
    assert entries["file2.txt"]["type"] == "file"
    assert entries["file2.txt"]["size"] > 0

def test_list_directory_not_found(client: TestClient, temp_fs: Path):
    """Test listing a non-existent directory."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {"jsonrpc": "2.0", "method": "listDirectory", "params": {"path": "/test_data/nonexistent"}, "id": "list_404"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200 # MCP errors are returned in JSON
    data = response.json()
    assert data.get("id") == "list_404"
    assert "error" in data
    assert data["error"]["code"] == -32602 # Invalid params (FileNotFoundError)
    assert "not a directory" in data["error"]["message"].lower()

def test_list_directory_forbidden(client: TestClient, temp_fs: Path):
    """Test listing a directory outside allowed paths."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {"jsonrpc": "2.0", "method": "listDirectory", "params": {"path": "/etc"}, "id": "list_forbidden"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "list_forbidden"
    assert "error" in data
    assert data["error"]["code"] == -32000 # Server error (PermissionError)
    assert "access denied" in data["error"]["message"].lower()

def test_read_file_success(client: TestClient, temp_fs: Path):
    """Test reading an existing file."""
    if client is None: pytest.skip("Client fixture failed")
    file_path = "/test_data/file1.txt"
    mcp_request = {"jsonrpc": "2.0", "method": "readFile", "params": {"path": file_path}, "id": "read_ok"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "read_ok"
    assert "result" in data
    assert data["result"]["path"] == file_path
    assert data["result"]["content"] == "Hello from file1"
    assert data["result"]["encoding"] == "utf-8"

def test_read_file_not_found(client: TestClient, temp_fs: Path):
    """Test reading a non-existent file."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {"jsonrpc": "2.0", "method": "readFile", "params": {"path": "/test_data/nosuchfile.txt"}, "id": "read_404"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "read_404"
    assert "error" in data
    assert data["error"]["code"] == -32602 # Invalid params (FileNotFoundError)
    assert "not a file" in data["error"]["message"].lower()

def test_read_file_forbidden(client: TestClient, temp_fs: Path):
    """Test reading a file outside allowed paths."""
    if client is None: pytest.skip("Client fixture failed")
    # Use a known forbidden path
    forbidden_path = "/etc/passwd"
    mcp_request = {"jsonrpc": "2.0", "method": "readFile", "params": {"path": forbidden_path}, "id": "read_forbidden"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "read_forbidden"
    assert "error" in data
    assert data["error"]["code"] == -32000
    assert "access denied" in data["error"]["message"].lower()

def test_write_file_success(client: TestClient, temp_fs: Path):
    """Test writing a new file."""
    if client is None: pytest.skip("Client fixture failed")
    file_path_in_request = "/test_data/new_file.txt"
    file_path_on_disk = temp_fs / "new_file.txt" # Path relative to the temp_fs fixture root
    content = "This is new content."
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "writeFile", 
        "params": {"path": file_path_in_request, "content": content},
        "id": "write_new"
    }
    response = client.post("/", json=mcp_request)
    print(f"Write response: {response.json()}") # Debug output
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "write_new"
    assert "result" in data
    assert data["result"]["path"] == file_path_in_request
    assert data["result"]["message"] == "File written successfully."
    # Verify file content on disk using the correct path
    assert file_path_on_disk.exists(), f"File {file_path_on_disk} was not created"
    assert file_path_on_disk.read_text() == content

def test_write_file_overwrite_success(client: TestClient, temp_fs: Path):
    """Test overwriting an existing file."""
    if client is None: pytest.skip("Client fixture failed")
    file_path_in_request = "/test_data/file1.txt"
    file_path_on_disk = temp_fs / "file1.txt"
    new_content = "Overwritten content."
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "writeFile", 
        "params": {"path": file_path_in_request, "content": new_content, "overwrite": True},
        "id": "write_overwrite"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "write_overwrite"
    assert "result" in data
    # Verify file content on disk
    assert file_path_on_disk.read_text() == new_content

def test_write_file_no_overwrite_fail(client: TestClient, temp_fs: Path):
    """Test writing to existing file fails when overwrite is false."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {
        "jsonrpc": "2.0", "method": "writeFile", 
        "params": {"path": "/test_data/file1.txt", "content": "fail", "overwrite": False},
        "id": "write_no_overwrite"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "write_no_overwrite"
    assert "error" in data
    assert data["error"]["code"] == -32602 # Invalid params (FileExistsError)
    assert "file already exists" in data["error"]["message"].lower()

def test_write_file_forbidden(client: TestClient, temp_fs: Path):
    """Test writing to a forbidden path."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {
        "jsonrpc": "2.0", "method": "writeFile", 
        "params": {"path": "/etc/shadow", "content": "test"},
        "id": "write_forbidden"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "write_forbidden"
    assert "error" in data
    assert data["error"]["code"] == -32000 # Server error (PermissionError)
    assert "write access denied" in data["error"]["message"].lower()

def test_write_file_create_parents(client: TestClient, temp_fs: Path):
    """Test writing a file and creating parent directories."""
    if client is None: pytest.skip("Client fixture failed")
    file_path_in_request = "/test_data/newdir/subdir/deep_file.txt"
    file_path_on_disk = temp_fs / "newdir" / "subdir" / "deep_file.txt"
    content = "Deep content"
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "writeFile", 
        "params": {"path": file_path_in_request, "content": content, "create_parents": True},
        "id": "write_parents"
    }
    response = client.post("/", json=mcp_request)
    print(f"Write (parents) response: {response.json()}") # Debug output
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "write_parents"
    assert "result" in data
    assert file_path_on_disk.exists(), f"File {file_path_on_disk} was not created"
    assert file_path_on_disk.read_text() == content
    assert file_path_on_disk.parent.is_dir()
    assert file_path_on_disk.parent.parent.is_dir()

# TODO: Add tests for read_only mode
# TODO: Add tests for delete, createDirectory, getFileInfo etc. when implemented

# --- Docker Container Integration Tests (Placeholder) ---
# Similar tests as above but using docker run and curl, need careful setup of volumes and ALLOWED_PATHS env var for the container.

def test_filesystem_docker_placeholder():
    """Placeholder for Docker tests for the filesystem server."""
    pytest.skip("Docker tests for filesystem MCP not implemented yet.") 