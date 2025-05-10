#!/usr/bin/env python3
# Memory Storage MCP - Core Application
# A memory storage server for AI agents with project-based organization and A2A compatibility

import os
import json
import logging
import time
import asyncio
import shutil
import datetime
from typing import Dict, List, Optional, Union, Any, cast
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import yaml
import schedule
from dotenv import load_dotenv

# Load environment variables from .env file if exists
load_dotenv()

# Configure logging
log_level = os.environ.get("MEMORY_STORAGE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("memory-storage-mcp")

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False
    },
    "storage": {
        "data_dir": "./data",
        "backup_dir": "./data/backups"
    },
    "security": {
        "enable_auth": False,
        "api_keys": []
    }
}

def load_config(config_file: Path = Path("config/config.yaml")) -> Dict[str, Any]:
    """
    Load configuration from a YAML file, falling back to defaults if not found.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Dict containing configuration
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = yaml.safe_load(f)
            
            # Merge file config with defaults
            if file_config:
                for section, values in file_config.items():
                    if section in config and isinstance(values, dict):
                        config[section].update(values)
                    else:
                        config[section] = values
                        
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")
    else:
        logger.warning(f"Configuration file {config_file} not found, using defaults")
    
    return config

def get_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables, falling back to defaults.
    
    Returns:
        Dict containing configuration
    """
    config = load_config()
    
    # Override with environment variables
    env_port = os.environ.get("MEMORY_STORAGE_PORT")
    if env_port:
        config["server"]["port"] = int(env_port)
    
    env_host = os.environ.get("MEMORY_STORAGE_HOST")
    if env_host:
        config["server"]["host"] = env_host
    
    env_debug = os.environ.get("MEMORY_STORAGE_DEBUG")
    if env_debug:
        config["server"]["debug"] = env_debug.lower() == "true"
    
    env_data_dir = os.environ.get("MEMORY_STORAGE_DATA_DIR")
    if env_data_dir:
        config["storage"]["data_dir"] = env_data_dir
    
    env_backup_dir = os.environ.get("MEMORY_STORAGE_BACKUP_DIR")
    if env_backup_dir:
        config["storage"]["backup_dir"] = env_backup_dir
    
    env_enable_auth = os.environ.get("MEMORY_STORAGE_AUTH_ENABLED")
    if env_enable_auth:
        config["security"]["enable_auth"] = env_enable_auth.lower() == "true"
    
    env_api_key = os.environ.get("MEMORY_STORAGE_AUTH_KEY")
    if env_api_key:
        config["security"]["api_keys"] = [env_api_key]
    
    return config

# Load configuration (but use environment variables with higher priority)
config = get_config()

# Load configuration
DATA_DIR = Path(os.environ.get("MEMORY_STORAGE_DATA_DIR", "./data"))
PORT = int(os.environ.get("MEMORY_STORAGE_PORT", 8000))
AUTH_ENABLED = os.environ.get("MEMORY_STORAGE_AUTH_ENABLED", "false").lower() == "true"
AUTH_KEY = os.environ.get("MEMORY_STORAGE_AUTH_KEY", "")
BACKUP_INTERVAL = int(os.environ.get("MEMORY_STORAGE_BACKUP_INTERVAL", 60))  # minutes

# Initialize FastAPI application
app = FastAPI(
    title="Memory Storage MCP",
    description="A memory storage server for AI agents with project-based organization",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProjectModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")

class FileModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    content: str

class BackupModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    comment: str = ""

class ProjectCreate(BaseModel):
    name: str

class ProjectInfo(BaseModel):
    name: str
    created_at: str
    file_count: int

class FileCreate(BaseModel):
    name: str
    content: str

class FileUpdate(BaseModel):
    content: str

class FileInfo(BaseModel):
    name: str
    size: int
    last_modified: str

class A2ARequest(BaseModel):
    action: str
    parameters: Dict[str, str]

# Authentication middleware
async def verify_auth(request: Request):
    if not AUTH_ENABLED:
        return True
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if token != AUTH_KEY:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return True

# Helper functions
def ensure_directory_exists(directory: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    directory.mkdir(parents=True, exist_ok=True)

def sanitize_name(name: str) -> str:
    """Sanitize a name to prevent path traversal attacks."""
    if not name or name.startswith(".") or "/" in name or "\\" in name or len(name) > 100:
        raise ValueError(f"Invalid name: {name}")
    return name

def get_project_path(project_name: str, base_dir: Path = DATA_DIR) -> Path:
    """Get the full path to a project directory."""
    sanitize_name(project_name)  # Validate name
    return base_dir / project_name

def get_file_path(project_name: str, file_name: str, base_dir: Path = DATA_DIR) -> Path:
    """Get the full path to a file within a project."""
    sanitize_name(project_name)  # Validate project name
    sanitize_name(file_name)     # Validate file name
    return get_project_path(project_name, base_dir) / file_name

def validate_project_exists(project_name: str, base_dir: Path = DATA_DIR) -> bool:
    """Validate that a project exists."""
    project_path = get_project_path(project_name, base_dir)
    if not project_path.exists() or not project_path.is_dir():
        raise FileNotFoundError(f"Project '{project_name}' not found")
    return True

def validate_file_exists(project_name: str, file_name: str, base_dir: Path = DATA_DIR) -> bool:
    """Validate that a file exists within a project."""
    validate_project_exists(project_name, base_dir)
    file_path = get_file_path(project_name, file_name, base_dir)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File '{file_name}' not found in project '{project_name}'")
    return True

def format_timestamp(timestamp: float) -> str:
    """Format a timestamp as ISO 8601 string."""
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

def create_backup(backup_name: str, comment: str = "", 
                 data_dir: Path = DATA_DIR, 
                 backup_dir: Path = None) -> str:
    """
    Create a backup of data.
    
    Args:
        backup_name: Name of the backup
        comment: Optional comment
        data_dir: Directory containing the data to back up
        backup_dir: Directory to store backups
        
    Returns:
        Full backup name with timestamp
    """
    if backup_dir is None:
        backup_dir = data_dir.parent / "backups"
    
    # Ensure backup directory exists
    ensure_directory_exists(backup_dir)
    
    # Create timestamped backup name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    full_backup_name = f"{backup_name}_{timestamp}"
    backup_path = backup_dir / full_backup_name
    
    # Create backup metadata
    metadata = {
        "name": backup_name,
        "timestamp": timestamp,
        "comment": comment,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Create backup directory
    backup_path.mkdir(parents=True)
    
    # Write metadata
    with open(backup_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Copy data
    if data_dir.exists():
        for item in data_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, backup_path / item.name)
            else:
                shutil.copy2(item, backup_path / item.name)
    
    return full_backup_name

def list_backups(backup_dir: Path) -> List[Dict[str, str]]:
    """
    List available backups.
    
    Args:
        backup_dir: Directory containing backups
    
    Returns:
        List of backup information dictionaries
    """
    backups = []
    
    if not backup_dir.exists():
        return backups
    
    for item in backup_dir.iterdir():
        if item.is_dir():
            metadata_path = item / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    
                    backups.append({
                        "name": item.name,
                        "created_at": metadata.get("created_at", ""),
                        "comment": metadata.get("comment", ""),
                        "size": sum(f.stat().st_size for f in item.glob("**/*") if f.is_file())
                    })
                except (json.JSONDecodeError, IOError):
                    # Include backup even if metadata is corrupted
                    backups.append({
                        "name": item.name,
                        "created_at": format_timestamp(item.stat().st_ctime),
                        "comment": "",
                        "size": sum(f.stat().st_size for f in item.glob("**/*") if f.is_file())
                    })
    
    # Sort by creation time (newest first)
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    return backups

def restore_backup(backup_name: str, data_dir: Path = DATA_DIR, 
                   backup_dir: Path = None) -> bool:
    """
    Restore a backup.
    
    Args:
        backup_name: Name of the backup to restore
        data_dir: Directory to restore data to
        backup_dir: Directory containing backups
        
    Returns:
        True if successful, False otherwise
    """
    if backup_dir is None:
        backup_dir = data_dir.parent / "backups"
    
    backup_path = backup_dir / backup_name
    
    if not backup_path.exists() or not backup_path.is_dir():
        raise FileNotFoundError(f"Backup '{backup_name}' not found")
    
    # Clear data directory
    if data_dir.exists():
        shutil.rmtree(data_dir)
    
    # Create empty data directory
    data_dir.mkdir(parents=True)
    
    # Copy backup data (excluding metadata)
    for item in backup_path.iterdir():
        if item.name != "metadata.json":
            if item.is_dir():
                shutil.copytree(item, data_dir / item.name)
            else:
                shutil.copy2(item, data_dir / item.name)
    
    return True

# API routes

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "Memory Storage MCP is running", "version": "1.0.0"}

@app.get("/projects", response_model=List[ProjectInfo])
async def list_projects(_: bool = Depends(verify_auth)):
    """List all projects."""
    try:
        # Ensure data directory exists
        ensure_directory_exists(DATA_DIR)
        
        projects = []
        for path in DATA_DIR.iterdir():
            if path.is_dir() and path.name != "backups":
                file_count = sum(1 for _ in path.glob("*") if _.is_file())
                projects.append({
                    "name": path.name,
                    "created_at": format_timestamp(path.stat().st_ctime),
                    "file_count": file_count
                })
        return projects
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/projects", response_model=dict)
async def create_project(project: ProjectCreate, _: bool = Depends(verify_auth)):
    """Create a new project."""
    try:
        # Ensure data directory exists
        ensure_directory_exists(DATA_DIR)
        
        # Validate project name
        sanitize_name(project.name)
        
        project_path = get_project_path(project.name)
        if project_path.exists():
            raise HTTPException(status_code=400, detail=f"Project '{project.name}' already exists")
        
        project_path.mkdir(parents=True, exist_ok=True)
        return {"status": "success", "message": f"Project '{project.name}' created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/projects/{project_name}", response_model=ProjectInfo)
async def get_project(project_name: str, _: bool = Depends(verify_auth)):
    """Get project details."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        file_count = sum(1 for _ in project_path.glob("*") if _.is_file())
        return {
            "name": project_path.name,
            "created_at": format_timestamp(project_path.stat().st_ctime),
            "file_count": file_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/projects/{project_name}")
async def delete_project(project_name: str, _: bool = Depends(verify_auth)):
    """Delete a project."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        shutil.rmtree(project_path)
        return {"status": "success", "message": f"Project '{project_name}' deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/projects/{project_name}/files", response_model=List[FileInfo])
async def list_files(project_name: str, _: bool = Depends(verify_auth)):
    """List all files in a project."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        files = []
        for path in project_path.glob("*"):
            if path.is_file():
                stat = path.stat()
                files.append({
                    "name": path.name,
                    "size": stat.st_size,
                    "last_modified": format_timestamp(stat.st_mtime)
                })
        return files
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/projects/{project_name}/files")
async def create_file(project_name: str, file: FileCreate, _: bool = Depends(verify_auth)):
    """Create a new file in a project."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        file_path = get_file_path(project_name, file.name)
        if file_path.exists():
            raise HTTPException(status_code=400, detail=f"File '{file.name}' already exists in project '{project_name}'")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file.content)
        
        return {"status": "success", "message": f"File '{file.name}' created in project '{project_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/projects/{project_name}/files/{file_name}")
async def read_file(project_name: str, file_name: str, _: bool = Depends(verify_auth)):
    """Read file content."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        file_path = get_file_path(project_name, file_name)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in project '{project_name}'")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        stat = file_path.stat()
        return {
            "name": file_name,
            "content": content,
            "size": stat.st_size,
            "last_modified": format_timestamp(stat.st_mtime)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/projects/{project_name}/files/{file_name}")
async def update_file(project_name: str, file_name: str, file_update: FileUpdate, _: bool = Depends(verify_auth)):
    """Update file content."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        file_path = get_file_path(project_name, file_name)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in project '{project_name}'")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_update.content)
        
        return {"status": "success", "message": f"File '{file_name}' updated in project '{project_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/projects/{project_name}/files/{file_name}")
async def delete_file(project_name: str, file_name: str, _: bool = Depends(verify_auth)):
    """Delete a file."""
    try:
        project_path = get_project_path(project_name)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        file_path = get_file_path(project_name, file_name)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in project '{project_name}'")
        
        file_path.unlink()
        return {"status": "success", "message": f"File '{file_name}' deleted from project '{project_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# A2A compatibility endpoint
@app.post("/a2a")
async def a2a_endpoint(request: A2ARequest, _: bool = Depends(verify_auth)):
    """Handle A2A requests."""
    try:
        action = request.action
        params = request.parameters
        
        if action == "list_projects":
            projects = await list_projects(_=True)
            return {"status": "success", "projects": [p["name"] for p in projects]}
        
        elif action == "list_project_files":
            if "projectName" not in params:
                raise HTTPException(status_code=400, detail="Missing required parameter: projectName")
            
            files = await list_files(params["projectName"], _=True)
            return {"status": "success", "files": [f["name"] for f in files]}
        
        elif action == "memory_bank_read":
            if "projectName" not in params or "fileName" not in params:
                raise HTTPException(status_code=400, detail="Missing required parameters: projectName and/or fileName")
            
            file_data = await read_file(params["projectName"], params["fileName"], _=True)
            return {
                "status": "success", 
                "content": file_data["content"],
                "metadata": {
                    "lastModified": file_data["last_modified"],
                    "size": file_data["size"]
                }
            }
        
        elif action == "memory_bank_write":
            if "projectName" not in params or "fileName" not in params or "content" not in params:
                raise HTTPException(status_code=400, detail="Missing required parameters: projectName, fileName, and/or content")
            
            # Check if project exists, create if not
            project_path = get_project_path(params["projectName"])
            if not project_path.exists():
                await create_project(ProjectCreate(name=params["projectName"]), _=True)
            
            # Check if file exists
            file_path = get_file_path(params["projectName"], params["fileName"])
            if file_path.exists():
                # Update existing file
                await update_file(params["projectName"], params["fileName"], FileUpdate(content=params["content"]), _=True)
            else:
                # Create new file
                await create_file(params["projectName"], FileCreate(name=params["fileName"], content=params["content"]), _=True)
            
            return {"status": "success", "message": f"File written to {params['projectName']}/{params['fileName']}"}
        
        elif action == "memory_bank_update":
            if "projectName" not in params or "fileName" not in params or "content" not in params:
                raise HTTPException(status_code=400, detail="Missing required parameters: projectName, fileName, and/or content")
            
            await update_file(params["projectName"], params["fileName"], FileUpdate(content=params["content"]), _=True)
            return {"status": "success", "message": f"File updated at {params['projectName']}/{params['fileName']}"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in A2A endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Startup and periodic tasks
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Memory Storage MCP")
    
    # Ensure directories exist
    ensure_directory_exists(DATA_DIR)
    BACKUP_DIR = DATA_DIR / "backups"
    ensure_directory_exists(BACKUP_DIR)
    
    # Start background tasks
    asyncio.create_task(run_periodic_backups())

async def run_periodic_backups():
    """Run periodic backups in the background."""
    while True:
        await asyncio.sleep(BACKUP_INTERVAL * 60)
        logger.info(f"Running scheduled backup")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        create_backup(f"auto_backup_{timestamp}", "Automatic scheduled backup")

# For direct execution
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True) 