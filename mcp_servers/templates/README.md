# MCP Server Templates

This directory contains templates and guidelines for creating and integrating new MCP servers into the MCP-Launchpad project.

## Overview

The templates provide a standardized structure and approach for implementing MCP servers, ensuring consistency, quality, and compatibility across all servers in the project.

## Templates Index

### Planning and Guidelines

- [SERVER_SELECTION_CRITERIA.md](SERVER_SELECTION_CRITERIA.md) - Criteria for selecting MCP servers for implementation
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Checklist for ensuring complete implementation
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Step-by-step plan for implementing a new server

### Structure Templates

- [SERVER_TEMPLATE.md](SERVER_TEMPLATE.md) - Overview of server structure and documentation requirements

### Code Templates

- [Dockerfile.template](Dockerfile.template) - Template for Docker configuration
- [docker-compose.yml.template](docker-compose.yml.template) - Template for Docker Compose
- [config/default.json.template](config/default.json.template) - Template for server configuration
- [src/app.py.template](src/app.py.template) - Template for main application code

### Test Templates

- [test_docker_integration.py](test_docker_integration.py) - Template for Docker integration tests
- [conftest.py](conftest.py) - Template for pytest fixtures and configuration

### Documentation Templates

- [tests_README.md](tests_README.md) - Template for test documentation

## Usage

To create a new MCP server:

1. Choose the server from the [PRIORITY_IMPLEMENTATION_PLAN.md](../PRIORITY_IMPLEMENTATION_PLAN.md)
2. Create a new directory in `mcp_servers/your_server_name/`
3. Copy the relevant templates into your server directory
4. Update the templates with your server-specific code and documentation
5. Follow the [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) to ensure completeness
6. Add tests based on the test templates
7. Update the main README.md to include your server in the catalog

## Best Practices

- Follow Python best practices (PEP 8, type hints, docstrings)
- Ensure comprehensive test coverage
- Provide clear, detailed documentation
- Optimize Docker configuration for security and efficiency
- Implement proper error handling
- Make configuration flexible through environment variables
- Support A2A compatibility for AI agent integration

## Contributing

If you'd like to improve these templates or suggest new ones, please see our [CONTRIBUTING.md](../../CONTRIBUTING.md) guide. 