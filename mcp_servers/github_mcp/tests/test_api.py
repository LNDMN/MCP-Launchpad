import pytest
from fastapi.testclient import TestClient
import json
import os

# Import the client fixture from conftest
from .conftest import client # client fixture implicitly handles app import and mock token

# --- Local FastAPI App Tests (using Placeholder Implementation) ---

def test_github_health_check(client: TestClient):
    """Test the GitHub server's /health endpoint."""
    if client is None: pytest.skip("Client fixture failed")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # Check if token is configured (should be, using the mock token)
    assert data["github_token_configured"] == True

def test_github_tools_list_local(client: TestClient):
    """Test the MCP tools/list method for the placeholder GitHub tools."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {"jsonrpc": "2.0", "method": "tools/list", "id": "gh_list_local"}
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("jsonrpc") == "2.0"
    assert data.get("id") == "gh_list_local"
    assert "result" in data
    assert "tools" in data["result"]
    tool_names = [t['name'] for t in data["result"]["tools"]]
    assert "list_repositories" in tool_names
    assert "get_issue" in tool_names
    assert "search_code" in tool_names

def test_placeholder_list_repositories(client: TestClient):
    """Test the placeholder list_repositories implementation."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "list_repositories", 
        "params": {"affiliation": "owner"}, # Param included for realism
        "id": "gh_list_repos_test"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "gh_list_repos_test"
    assert "result" in data
    assert "repositories" in data["result"]
    assert len(data["result"]["repositories"]) == 2 # Matches placeholder
    assert data["result"]["repositories"][0]["name"] == "placeholder-repo-1"

def test_placeholder_get_issue(client: TestClient):
    """Test the placeholder get_issue implementation."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "get_issue", 
        "params": {"owner": "test", "repo": "test", "number": 123}, # Params included
        "id": "gh_get_issue_test"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == "gh_get_issue_test"
    assert "result" in data
    assert "issue" in data["result"]
    assert data["result"]["issue"]["number"] == 123
    assert data["result"]["issue"]["title"] == "Placeholder Issue"

def test_method_not_implemented(client: TestClient):
    """Test calling a method not present in the placeholder."""
    if client is None: pytest.skip("Client fixture failed")
    mcp_request = {
        "jsonrpc": "2.0", 
        "method": "create_pull_request", 
        "params": {},
        "id": "gh_not_impl_test"
    }
    response = client.post("/", json=mcp_request)
    assert response.status_code == 200 # MCP errors returned in JSON
    data = response.json()
    assert data.get("id") == "gh_not_impl_test"
    assert "error" in data
    assert data["error"]["code"] == -32601 # Method not found
    assert "not implemented" in data["error"]["message"].lower()

# --- Docker Container Integration Tests (Placeholder) ---

@pytest.mark.skip(reason="Requires actual GitHub MCP server code and Docker build/run with real or mock token")
def test_github_docker_placeholder():
    """Placeholder for Docker tests for the GitHub server."""
    pass 