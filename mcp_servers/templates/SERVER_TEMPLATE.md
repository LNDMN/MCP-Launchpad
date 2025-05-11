# MCP Server Template

This directory contains a template for adding new MCP servers to the MCP-Launchpad project.

## Directory Structure

When implementing a new MCP server, follow this directory structure:

```
mcp_servers/your_server_name/
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Optional: For multi-container setups
├── README.md                   # General documentation
├── AGENT_DOCS.md               # AI-friendly documentation (optional if included in README)
├── LICENSE                     # License information
├── requirements.txt            # Python dependencies (if applicable)
├── requirements-dev.txt        # Development dependencies
├── config/                     # Configuration files
│   └── default.json            # Default configuration
├── scripts/                    # Helper scripts
│   ├── run_tests.sh            # Test runner script
│   └── setup.sh                # Setup script
├── src/                        # Source code
│   ├── __init__.py             # Package initialization
│   ├── app.py                  # Main application
│   ├── models.py               # Data models
│   ├── api.py                  # API endpoints
│   └── utils.py                # Utility functions
└── tests/                      # Test suite
    ├── README.md               # Test documentation
    ├── conftest.py             # Test fixtures
    ├── test_api.py             # API tests
    ├── test_models.py          # Model tests
    ├── test_utils.py           # Utility tests
    └── test_docker_integration.py # Docker integration tests
```

## Implementation Steps

1. **Create directory structure**: Set up the directory with all necessary files
2. **Implement core functionality**: Develop the MCP server functionality
3. **Create Docker configuration**: Define Dockerfile and docker-compose.yml
4. **Write documentation**: Create README.md and AGENT_DOCS.md
5. **Add tests**: Implement comprehensive test suite
6. **Validate A2A compatibility**: Ensure Agent-to-Agent compatibility
7. **Update main README**: Add server to the catalog in the main README.md

## Dockerfile Requirements

Your Dockerfile should follow these best practices:

```dockerfile
# Use a specific version for stability
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Description of your MCP server"
LABEL version="1.0.0"

# Use a non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV CONFIG_PATH=/app/config/default.json

# Expose the port
EXPOSE 8000

# Switch to non-root user
USER mcp

# Set the entrypoint
CMD ["python", "-m", "src.app"]
```

## README.md Template

Your README.md should include the following sections:

```markdown
# YourServerName MCP Server

Short description of what the server does and its primary purpose.

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Prerequisites

- Requirement 1
- Requirement 2

## Quick Start

### Using Docker

```bash
docker run -p 8000:8000 -e ENV_VAR=value your-server-name:latest
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Configuration

The server can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port the server listens on | `8000` |
| `CONFIG_PATH` | Path to config file | `/app/config/default.json` |
| ... | ... | ... |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/resource` | GET | Get resources |
| `/api/resource` | POST | Create resource |
| ... | ... | ... |

## A2A Compatibility

This MCP server supports Agent-to-Agent communication. Examples:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your request here"
    }
  ]
}
```

## Data Persistence

Data is stored in:

- Location: `/app/data`
- Format: JSON/SQLite/etc.

Mount this directory as a volume for persistence:

```bash
docker run -v ./data:/app/data -p 8000:8000 your-server-name:latest
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/your-server-name.git

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Build Docker image
docker build -t your-server-name:latest .
```

## License

This project is licensed under the [License Name](LICENSE) - see the LICENSE file for details.

## Original Source

This server is adapted from [Original Repository](https://github.com/original/repo) with modifications to meet MCP-Launchpad standards.
```

## AGENT_DOCS.md Template

In addition to the general README, you should provide AI-friendly documentation specifically designed for AI agents:

```markdown
# YourServerName MCP Server for AI Agents

This document is specifically designed for AI agents to understand how to interact with the YourServerName MCP server.

## Overview

YourServerName is a MCP server that [brief description]. Use this server when you need to [primary use case].

## Capabilities

- **Capability 1**: [Description with example]
- **Capability 2**: [Description with example]
- **Capability 3**: [Description with example]

## Quick Reference

| Task | Command/Endpoint | Example |
|------|------------------|---------|
| Task 1 | `/api/endpoint1` | `{"param": "value"}` |
| Task 2 | `/api/endpoint2` | `{"param": "value"}` |
| Task 3 | `/api/endpoint3` | `{"param": "value"}` |

## Standard Workflow

1. **Step 1**: [Description]
   ```json
   // Example request
   {
     "param": "value"
   }
   ```

2. **Step 2**: [Description]
   ```json
   // Example request
   {
     "param": "value"
   }
   ```

3. **Step 3**: [Description]
   ```json
   // Example request
   {
     "param": "value"
   }
   ```

## Error Handling

Common errors and their solutions:

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Bad Request | [Solution] |
| 401 | Unauthorized | [Solution] |
| 404 | Not Found | [Solution] |
| 500 | Server Error | [Solution] |

## Integration Example

Complete example of using this MCP server in an AI agent workflow:

```json
// A2A request example
{
  "messages": [
    {
      "role": "user",
      "content": "Your request here"
    }
  ]
}
```

Expected response:

```json
{
  "result": "Example result"
}
```
```

## Docker Integration Tests

Ensure you implement thorough Docker integration tests based on our template:

```python
# See mcp_servers/templates/test_docker_integration.py for a complete example
```

## Updating the Catalog

After implementing your MCP server, update the main README.md to include your server in the catalog with the appropriate progress indicators. 