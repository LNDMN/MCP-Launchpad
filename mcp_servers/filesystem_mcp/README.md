# Local Filesystem MCP Server (MCP-Launchpad Adaptation)

## Purpose
This MCP server provides secure access to the local filesystem for AI agents. It allows agents to perform operations like reading files, writing files, listing directories, and potentially other file manipulations within predefined, safe boundaries.

This server is designed to be run locally and configured to grant access only to specified paths, enhancing security.

## Key Features/Endpoints/Commands
*(To be implemented/detailed)*
- **`readFile`**: Reads the content of a file.
- **`writeFile`**: Writes content to a file (potentially creating it).
- **`listDirectory`**: Lists files and subdirectories within a directory.
- **`getFileInfo`**: Gets metadata about a file (size, modification date, etc.).
- **`deleteFile`**: Deletes a file.
- **`createDirectory`**: Creates a new directory.
- ... (Other potential file operations)

## A2A Compatibility
*(To be confirmed/detailed)*
- Describe A2A support if implemented.

## Docker Launch Command
```bash
# Ensure Docker is installed
# Navigate to the MCP-Launchpad root directory

# Build the image
docker build -t mcp/filesystem mcp_servers/filesystem_mcp/

# Run the container - CRITICAL: Mount the host directory you want to expose
# Example: Expose /home/user/shared_files on the host as /data inside the container
docker run -d --name filesystem_mcp -p 8081:8000 \
  -v /path/on/host/to/expose:/data:rw \
  -e ALLOWED_PATHS=/data \
  mcp/filesystem
```
**Security Note:** Carefully configure the `ALLOWED_PATHS` environment variable and the volume mount (`-v`) to restrict agent access to only necessary directories.
*(Adjust port mapping (8081:8000) and volume mounts as needed)*

## Environment Variables
- **`MCP_PORT`**: Port inside the container (default: 8000).
- **`ALLOWED_PATHS`**: Comma-separated list of absolute paths *inside the container* that the agent is allowed to access (e.g., `/data,/app/config`). Mandatory for security.
- **`READ_ONLY`**: Set to `true` to restrict operations to read-only (list, read, getInfo). (Default: `false`).
- `LOG_LEVEL`: Logging level (e.g., INFO, DEBUG).

## Example Usage
*(To be filled in)*
**Example MCP Request (Conceptual):**
```json
{
  "jsonrpc": "2.0",
  "method": "readFile",
  "params": {
    "path": "/data/mydocument.txt" 
  },
  "id": 123
}
```
**Expected Response (Conceptual):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": "File content here...",
    "encoding": "utf-8",
    "path": "/data/mydocument.txt"
  },
  "id": 123
}
```

## Data Persistence
Data persistence is managed by mounting host directories into the container using Docker volumes (`-v`). The server itself is stateless.

## Licensing
- **Original MCP Server:** To be developed (or sourced). License: TBD (Likely MIT if developed internally).
- **Dockerfile & Documentation (This Repository):** MIT License.

## Original Source
- **GitHub Repository:** This repository (if developed internally) or link to original source if adapted. 