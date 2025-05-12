# Microsoft Playwright MCP Server (MCP-Launchpad Adaptation)

## Purpose
This MCP server provides tools for AI agents to automate and interact with web browsers using Microsoft Playwright. It enables capabilities like web navigation, data extraction, form filling, and interaction with web page elements through structured accessibility snapshots.

This specific implementation is adapted for the MCP-Launchpad project, ensuring easy deployment and integration within our ecosystem.

## Key Features/Endpoints/Commands
*(To be filled in once the server code is integrated)*
- **Navigate:** Go to a specific URL.
- **Click:** Interact with an element (button, link, etc.).
- **Input:** Fill text into input fields.
- **Query Selector:** Find elements on the page.
- **Get Content:** Extract text or HTML content.
- **Take Screenshot:** Capture the current page view.
- ... (List other relevant commands/API endpoints)

## A2A Compatibility
*(To be confirmed/detailed)*
- Describe if and how this server supports Agent-to-Agent communication.
- Provide example A2A request/response formats if applicable.

## Docker Launch Command
```bash
# Ensure you have Docker installed
# Navigate to the MCP-Launchpad root directory

# Build the image (if not already built)
docker build -t mcp/playwright mcp_servers/playwright_mcp/

# Run the container
docker run -d --name playwright_mcp -p 8080:8000 \
  -v playwright_mcp_data:/app/data \ # Example for persistent data if needed
  # Add any necessary environment variables using -e KEY=VALUE
  mcp/playwright
```
*(Adjust port mapping (8080:8000) and volume mounts as needed)*

## Environment Variables
*(To be detailed based on implementation)*
- `MCP_PORT`: Port the server listens on (default: 8000 inside container).
- `LOG_LEVEL`: Logging level (e.g., INFO, DEBUG).
- ... (List all required and optional environment variables)

## Example Usage
*(To be filled in with concrete examples)*
**Example MCP Request (Conceptual):**
```json
{
  "tool_name": "navigate_browser",
  "parameters": {
    "url": "https://example.com"
  }
}
```
**Expected Response (Conceptual):**
```json
{
  "status": "success",
  "message": "Successfully navigated to https://example.com",
  "page_title": "Example Domain"
}
```

## Data Persistence
*(Specify if the server requires persistent storage and how to manage it, e.g., using Docker volumes)*
- Example: Browser session data, downloaded files, etc.

## Licensing
- **Original MCP Server:** [Microsoft Playwright MCP License](https://github.com/microsoft/playwright-mcp/blob/main/LICENSE) *(Link to be verified)* - Please verify the exact license from the original source.
- **Dockerfile & Documentation (This Repository):** MIT License (See main project LICENSE file).

## Original Source
- **GitHub Repository:** [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) 