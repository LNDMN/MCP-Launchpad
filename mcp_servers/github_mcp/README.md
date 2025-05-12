# GitHub MCP Server (MCP-Launchpad Adaptation)

**Original Source:** [github/github-mcp-server](https://github.com/github/github-mcp-server)
**Original License:** MIT License

## Purpose
This MCP server acts as a bridge between AI agents and the GitHub API. It allows agents to perform various GitHub operations like listing repositories, reading files, managing issues and pull requests, searching code, and interacting with other GitHub resources programmatically.

This adaptation integrates the official GitHub MCP server into the MCP-Launchpad framework for standardized deployment and usage.

## Key Features/Endpoints/Commands
(Based on the official `github-mcp-server` tools - list might be extensive)
- **Repository Management:** `list_repositories`, `get_repository`, `get_readme`, `get_file_content`, `list_branches`, `list_commits`...
- **Issue Tracking:** `list_issues`, `get_issue`, `create_issue`, `update_issue`, `list_issue_comments`, `add_issue_comment`...
- **Pull Requests:** `list_pull_requests`, `get_pull_request`, `create_pull_request`, `update_pull_request`, `list_pr_files`, `list_pr_comments`, `add_pr_comment`...
- **Code Search:** `search_code`
- **User Interaction:** `get_user`, `search_users`...
- **And many more...** (Refer to the original server's documentation or `tools/list` method for a complete list)

## A2A Compatibility
- Expected to be fully compatible via standard MCP JSON-RPC calls.

## Docker Launch Command
```bash
# Ensure Docker is installed
# Navigate to the MCP-Launchpad root directory

# Build the image
docker build -t mcp/github mcp_servers/github_mcp/

# Run the container - Requires GitHub Token
# Option 1: Pass token as environment variable (less secure)
docker run -d --name github_mcp -p 8082:8000 \
  -e GITHUB_TOKEN=YOUR_GITHUB_PAT \
  mcp/github

# Option 2: Mount token from a file (more secure)
# echo "YOUR_GITHUB_PAT" > /path/to/github_token.txt
# docker run -d --name github_mcp -p 8082:8000 \
#   -v /path/to/github_token.txt:/run/secrets/github_token:ro \
#   -e GITHUB_TOKEN_PATH=/run/secrets/github_token \
#   mcp/github 
```
*(Adjust port mapping (8082:8000) as needed. Replace `YOUR_GITHUB_PAT` with your actual GitHub Personal Access Token with appropriate permissions.)*

## Environment Variables
- **`GITHUB_TOKEN`**: Your GitHub Personal Access Token (PAT). Required for most operations.
- **`GITHUB_TOKEN_PATH`**: Path to a file inside the container containing the GitHub PAT (alternative to `GITHUB_TOKEN`).
- **`MCP_PORT`**: Port inside the container (default: 8000).
- `LOG_LEVEL`: Logging level (e.g., INFO, DEBUG).
- `GITHUB_API_URL`: GitHub API URL (optional, defaults to `https://api.github.com`, use for GitHub Enterprise).

## Example Usage
**Example MCP Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "list_repositories",
  "params": {
    "affiliation": "owner"
  },
  "id": "gh-list-repos-1"
}
```
**Expected Response (Conceptual):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "repositories": [
      {"name": "MCP-Launchpad", "full_name": "YourUser/MCP-Launchpad", ...},
      ...
    ]
  },
  "id": "gh-list-repos-1"
}
```

## Data Persistence
This server is generally stateless, relying on the GitHub API for all data.

## Licensing
- **Original MCP Server (`github/github-mcp-server`):** MIT License.
- **Dockerfile & Documentation (This Repository):** MIT License. 