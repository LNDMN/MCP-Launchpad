# Stage 1: Build stage with uv
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock* ./ 
# Ensure uv.lock is present or handle its absence if optional
# For now, assuming uv.lock is always present or pyproject.toml is enough for `uv sync`
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY src/ ./src/
RUN uv sync --frozen --no-dev --no-editable

# Stage 2: Final stage
FROM python:3.13-slim-bookworm

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r mcpuser && useradd --no-log-init -r -g mcpuser mcpuser

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=mcpuser:mcpuser /app/.venv /app/.venv
# Copy the source code
COPY --from=builder --chown=mcpuser:mcpuser /app/src /app/src

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to the non-root user
USER mcpuser

# Expose a default port (e.g., 8091, will need to confirm from server implementation)
EXPOSE 8091

# Run mcp server
# The actual script might be server.py or main.py inside src/mcp_text_editor
ENTRYPOINT ["python", "-m", "mcp_text_editor.server"] 
# Default CMD with a common port and allowing external connections.
# --base-directory will need to be passed by the user via `docker run -v` and this CMD or overridden.
CMD ["--port", "8091", "--host", "0.0.0.0", "--base-directory", "/workspace"] 