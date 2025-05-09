# 🧠 Memory Storage MCP

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)]() [![A2A](https://img.shields.io/badge/A2A-Compatible-brightgreen.svg)]() [![OS](https://img.shields.io/badge/OS-Cross--Platform-lightgrey.svg)]() [![Language](https://img.shields.io/badge/Language-Python-yellow.svg)]()

A lightweight, persistent, and high-performance storage solution for AI-agent memory and context management. Designed for seamless integration with AI workflows, it offers structured storage for short and long-term memory with hierarchical organization capabilities.

## 🌟 Key Features

- **Multi-layered Memory Storage**: Support for different memory types (SHORT_TERM, LONG_TERM, PROJECT, GLOBAL)
- **Project-Based Organization**: Hierarchical structure for organized memory management
- **Full CRUD Operations**: Create, read, update, and delete memory records
- **REST API & A2A Interface**: Easy integration with any AI agent or system
- **JSON Document Storage**: Flexible schema for diverse memory structures
- **Automatic Persistence**: Built-in backup and restore capabilities
- **Multi-user Support**: Isolated memory spaces for different agents or users
- **Low Latency**: Optimized for quick memory access and updates

## 📋 Usage for AI Agents

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects` | GET | List all projects |
| `/projects` | POST | Create a new project |
| `/projects/{project_name}` | GET | Get project details |
| `/projects/{project_name}` | DELETE | Delete a project |
| `/projects/{project_name}/files` | GET | List all files in a project |
| `/projects/{project_name}/files` | POST | Create a new file |
| `/projects/{project_name}/files/{file_name}` | GET | Read file content |
| `/projects/{project_name}/files/{file_name}` | PUT | Update file content |
| `/projects/{project_name}/files/{file_name}` | DELETE | Delete a file |

### A2A Mode

In A2A-compatible mode, the server accepts standard agent-to-agent communication formats. Example request:

```json
{
  "action": "memory_bank_read",
  "parameters": {
    "projectName": "AI_PROJECT_X",
    "fileName": "context_data.md"
  }
}
```

Example response:

```json
{
  "status": "success",
  "content": "# Project Context\n\nThis is the context for AI_PROJECT_X...",
  "metadata": {
    "lastModified": "2023-07-15T10:30:45Z",
    "size": 1254,
    "format": "markdown"
  }
}
```

## 🐳 Docker Deployment

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMORY_STORAGE_PORT` | Port for the API server | `8000` |
| `MEMORY_STORAGE_DATA_DIR` | Directory to store memory data | `/data` |
| `MEMORY_STORAGE_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MEMORY_STORAGE_BACKUP_INTERVAL` | Automatic backup interval (minutes) | `60` |
| `MEMORY_STORAGE_AUTH_ENABLED` | Enable authentication | `false` |
| `MEMORY_STORAGE_AUTH_KEY` | Auth key when authentication is enabled | `""` |

### Simple Launch

```bash
docker run -d \
  --name memory-storage-mcp \
  -p 8000:8000 \
  -v memory_data:/data \
  memory-storage-mcp:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## 💾 Data Persistence

Memory data is stored in a volume mounted at `/data` inside the container. To ensure your data persists between container restarts:

```bash
docker volume create memory_data
```

You can also mount a local directory for direct access to memory files:

```bash
docker run -d \
  --name memory-storage-mcp \
  -p 8000:8000 \
  -v /path/on/host:/data \
  memory-storage-mcp:latest
```

## 🛡️ Security Considerations

By default, authentication is disabled for easier development and local use. For production environments, enable authentication:

```bash
docker run -d \
  --name memory-storage-mcp \
  -p 8000:8000 \
  -v memory_data:/data \
  -e MEMORY_STORAGE_AUTH_ENABLED=true \
  -e MEMORY_STORAGE_AUTH_KEY=your_secret_key \
  memory-storage-mcp:latest
```

## 📄 License

This MCP server is released under the MIT License. See the LICENSE file for details.

## 🔍 Troubleshooting

**Common Issues:**

- **Cannot connect to server**: Ensure port 8000 is not blocked by firewall
- **Data not persisting**: Verify volume mounting is correct
- **Slow performance**: Consider increasing container resources for large memory storage

For additional help, check the logs:

```bash
docker logs memory-storage-mcp
``` 