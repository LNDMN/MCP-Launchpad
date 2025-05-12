from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
import stat
import logging
import json
from pathlib import Path

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# --- Configuration & Security --- 
def get_allowed_paths() -> List[Path]:
    """Gets and validates allowed paths from environment variable."""
    allowed_paths_str = os.environ.get("ALLOWED_PATHS")
    if not allowed_paths_str:
        logger.error("CRITICAL: ALLOWED_PATHS environment variable is not set. Filesystem access is disabled.")
        return []
    
    # Use absolute paths inside the container context
    paths = [Path(p.strip()).resolve() for p in allowed_paths_str.split(',') if p.strip()]
    logger.info(f"Allowed paths configured: {paths}")
    # Basic validation: check if paths exist (might need adjustment based on container setup)
    # for p in paths: 
    #     if not p.exists():
    #         logger.warning(f"Configured allowed path does not exist: {p}")
    return paths

ALLOWED_PATHS = get_allowed_paths()
IS_READ_ONLY = os.environ.get("READ_ONLY", "false").lower() == "true"
if IS_READ_ONLY:
    logger.warning("Server is running in READ-ONLY mode.")

def is_path_allowed(target_path: Path) -> bool:
    """Checks if the target path is within one of the allowed directories."""
    if not ALLOWED_PATHS:
        return False # No access if ALLOWED_PATHS is not configured
    
    resolved_target = target_path.resolve()
    logger.debug(f"Checking path: {resolved_target}")
    
    for allowed_dir in ALLOWED_PATHS:
        try:
            # Check if the resolved target path is relative to the allowed directory
            # This prevents path traversal (e.g., /data/../etc/passwd)
            resolved_target.relative_to(allowed_dir)
            logger.debug(f"{resolved_target} is within {allowed_dir}")
            return True
        except ValueError:
            # Path is not within this allowed directory, check the next one
            continue 
            
    logger.warning(f"Access denied for path: {resolved_target}. Not within allowed: {ALLOWED_PATHS}")
    return False

# --- FastAPI App --- 
app = FastAPI(
    title="Local Filesystem MCP Server (MCP-Launchpad)",
    description="Provides secure, restricted access to the local filesystem.",
    version="0.1.0",
)

# --- MCP JSON-RPC Models --- 
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] | List[Any] | None = None
    id: str | int | None = None

class MCPErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    error: Dict[str, Any]
    id: Optional[str | int] = None

class MCPSuccessResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Dict[str, Any]
    id: Optional[str | int] = None


# --- Tool Implementations --- 

async def list_directory(params: Dict[str, Any]) -> Dict[str, Any]:
    path_str = params.get("path")
    if not path_str:
        raise ValueError("Missing 'path' parameter")
    
    target_path = Path(path_str)
    if not is_path_allowed(target_path):
        raise PermissionError(f"Access denied for path: {target_path}")
    
    if not target_path.is_dir():
        raise FileNotFoundError(f"Path is not a directory: {target_path}")

    entries = []
    for entry in target_path.iterdir():
        try:
            # Get basic stats, handle potential permission errors
            info = entry.stat()
            entry_type = "directory" if entry.is_dir() else "file"
            entries.append({
                "name": entry.name,
                "path": str(entry.resolve()),
                "type": entry_type,
                "size": info.st_size,
                "modified_at": info.st_mtime # POSIX timestamp
            })
        except OSError as e:
            logger.warning(f"Could not access entry {entry.name}: {e}")
            entries.append({"name": entry.name, "error": str(e)})
            
    return {"path": str(target_path.resolve()), "entries": entries}

async def read_file(params: Dict[str, Any]) -> Dict[str, Any]:
    path_str = params.get("path")
    encoding = params.get("encoding", "utf-8")
    if not path_str:
        raise ValueError("Missing 'path' parameter")

    target_path = Path(path_str)
    if not is_path_allowed(target_path):
        raise PermissionError(f"Access denied for path: {target_path}")

    if not target_path.is_file():
        raise FileNotFoundError(f"Path is not a file: {target_path}")

    try:
        content = target_path.read_text(encoding=encoding)
        return {
            "path": str(target_path.resolve()),
            "content": content,
            "encoding": encoding,
            "size": target_path.stat().st_size
        }
    except Exception as e:
        logger.error(f"Error reading file {target_path}: {e}")
        raise # Re-raise to be caught by the dispatcher

async def write_file(params: Dict[str, Any]) -> Dict[str, Any]:
    if IS_READ_ONLY:
        raise PermissionError("Write operations are disabled (READ_ONLY mode)")
        
    path_str = params.get("path")
    content = params.get("content")
    encoding = params.get("encoding", "utf-8")
    overwrite = params.get("overwrite", False)
    create_parents = params.get("create_parents", False)

    if not path_str or content is None:
        raise ValueError("Missing 'path' or 'content' parameter")

    target_path = Path(path_str)
    
    # Security check: Allow writing *only if* the intended path resolves within an allowed dir.
    # This also implicitly checks the parent directory for creation.
    allowed_dir_for_write = None
    resolved_target = target_path.resolve()
    for allowed_dir in ALLOWED_PATHS:
        try:
            resolved_target.relative_to(allowed_dir)
            # Check if the *immediate* parent exists and is within allowed paths OR if create_parents is true
            parent_dir = resolved_target.parent
            if parent_dir.exists() and is_path_allowed(parent_dir):
                 allowed_dir_for_write = allowed_dir
                 break
            elif create_parents and is_path_allowed(parent_dir): # Check parent even if it doesn't exist yet
                 allowed_dir_for_write = allowed_dir
                 break
            else:
                 logger.warning(f"Parent directory {parent_dir} not allowed or does not exist (and create_parents=false)")
        except ValueError:
            continue
            
    if not allowed_dir_for_write:
        raise PermissionError(f"Write access denied for path: {target_path} (or its parent)")

    if target_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists and overwrite is false: {target_path}")
    
    if target_path.is_dir():
         raise IsADirectoryError(f"Cannot write file, path is a directory: {target_path}")

    try:
        if create_parents:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            # Re-verify parent permissions after creation (though checked above)
            if not is_path_allowed(target_path.parent):
                 raise PermissionError(f"Could not create allowed parent directory for: {target_path}")
                 
        target_path.write_text(content, encoding=encoding)
        logger.info(f"Successfully wrote to file: {target_path}")
        return {
            "path": str(target_path.resolve()),
            "size": target_path.stat().st_size,
            "message": "File written successfully."
        }
    except Exception as e:
        logger.error(f"Error writing file {target_path}: {e}")
        raise

# --- MCP Endpoint --- 

@app.post("/", response_model=None, tags=["MCP"], summary="MCP JSON-RPC Endpoint")
async def handle_mcp_request(request: MCPRequest) -> Dict[str, Any]:
    
    tool_map = {
        "tools/list": lambda p: { # Provide basic tool listing
            "tools": [
                {"name": "listDirectory", "description": "Lists files and subdirectories in a directory.", "parameters": {"path": "string"}},
                {"name": "readFile", "description": "Reads the content of a file.", "parameters": {"path": "string", "encoding": "string (optional, default utf-8)"}},
                {"name": "writeFile", "description": "Writes content to a file.", "parameters": {"path": "string", "content": "string", "encoding": "string (optional)", "overwrite": "boolean (optional)", "create_parents": "boolean (optional)"}},
                # Add other tools here
            ]
        },
        "listDirectory": list_directory,
        "readFile": read_file,
        "writeFile": write_file,
        # Add other method mappings here
    }

    func = tool_map.get(request.method)

    if not func:
        logger.warning(f"Method not found: {request.method}")
        error_details = {"code": -32601, "message": f"Method not found: {request.method}"}
        return MCPErrorResponse(error=error_details, id=request.id).model_dump(exclude_none=True)
        
    # Check allowed paths configuration
    if not ALLOWED_PATHS and request.method != "tools/list":
         logger.error(f"Attempted file operation '{request.method}' but ALLOWED_PATHS is not set.")
         error_details = {"code": -32001, "message": "Server configuration error: ALLOWED_PATHS not set."}
         return MCPErrorResponse(error=error_details, id=request.id).model_dump(exclude_none=True)

    try:
        # Assume params are a dict for filesystem tools
        params_dict = request.params if isinstance(request.params, dict) else {}
        if params_dict is None: params_dict = {}
        
        result_data = await func(params_dict)
        logger.debug(f"Method {request.method} executed successfully.")
        return MCPSuccessResponse(result=result_data, id=request.id).model_dump(exclude_none=True)

    except (ValueError, FileNotFoundError, FileExistsError, IsADirectoryError, TypeError) as e:
        logger.warning(f"Client error for method {request.method}: {e}")
        error_details = {"code": -32602, "message": f"Invalid parameters: {e}"}
        return MCPErrorResponse(error=error_details, id=request.id).model_dump(exclude_none=True)
        
    except PermissionError as e:
        logger.error(f"Permission error for method {request.method}: {e}")
        error_details = {"code": -32000, "message": f"Server error: {e}"}
        return MCPErrorResponse(error=error_details, id=request.id).model_dump(exclude_none=True)
        
    except Exception as e:
        logger.exception(f"Unexpected server error for method {request.method}: {e}") # Log traceback
        error_details = {"code": -32000, "message": f"Unexpected server error: {type(e).__name__}"}
        return MCPErrorResponse(error=error_details, id=request.id).model_dump(exclude_none=True)

# Health check endpoint
@app.get("/health", tags=["Status"])
def health_check():
    # Basic health check, could be expanded later
    return {"status": "ok", "read_only": IS_READ_ONLY, "allowed_paths_configured": bool(ALLOWED_PATHS)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Filesystem MCP server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("MCP_PORT", 8000))) 