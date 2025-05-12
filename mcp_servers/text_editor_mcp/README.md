# Text Editor MCP Server (Adapter for tumf/mcp-text-editor)

**Original Source:** [tumf/mcp-text-editor](https://github.com/tumf/mcp-text-editor)
**License:** MIT (see [LICENSE](LICENSE) file)

## Purpose

This MCP server provides tools for AI agents to interact with text files in a line-oriented manner. It is optimized for LLM tools, offering efficient partial file access to minimize token usage when reading or modifying large files.

## Key Features/Endpoints/Commands

(Based on typical text editing operations and the project's description - to be confirmed after reviewing the source)

- **`text_read_lines`**: Reads a specific range of lines from a file.
- **`text_write_lines`**: Writes or overwrites a range of lines in a file.
- **`text_insert_lines`**: Inserts lines at a specific position in a file.
- **`text_delete_lines`**: Deletes a range of lines from a file.
- **`text_get_line_count`**: Gets the total number of lines in a file.
- **`file_list_directory`**: (Potentially, if it supports basic file browsing)
- **`file_read_file`**: (Potentially, for reading entire small files)
- **`file_write_file`**: (Potentially, for writing entire small files)

*The server is optimized for partial file access.*

## A2A Compatibility

(Details to be filled in)

## Docker Launch Command

```bash
# (To be provided after Dockerfile creation)
docker run -p <host_port>:<container_port> -v /path/on/host:/data_directory_in_container <image_name> --root-dir /data_directory_in_container
```

## Environment Variables

| Variable             | Description                                                                 | Default        | Required |
|----------------------|-----------------------------------------------------------------------------|----------------|----------|
| `MCP_EDITOR_ROOT_DIR`| The root directory within the container that the server has access to.      | `/workspace`   | Yes      |
| `MCP_EDITOR_PORT`    | Port the server listens on.                                                 | (e.g., 8091)   | No       |

## Example Usage

(To be provided)

## Data Persistence

Data persistence is managed by mounting a host directory into the container. 