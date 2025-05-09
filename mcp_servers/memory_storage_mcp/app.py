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
from typing import Dict, List, Optional, Union
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import yaml
import schedule

# Configure logging
log_level = os.environ.get("MEMORY_STORAGE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("memory-storage-mcp")

# Load configuration
DATA_DIR = Path(os.environ.get("MEMORY_STORAGE_DATA_DIR", "/data"))
PORT = int(os.environ.get("MEMORY_STORAGE_PORT", 8000))
AUTH_ENABLED = os.environ.get("MEMORY_STORAGE_AUTH_ENABLED", "false").lower() == "true"
AUTH_KEY = os.environ.get("MEMORY_STORAGE_AUTH_KEY", "")
BACKUP_INTERVAL = int(os.environ.get("MEMORY_STORAGE_BACKUP_INTERVAL", 60))  # minutes

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

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
def get_project_path(project_name: str) -> Path:
    """Get the full path to a project directory."""
    project_path = DATA_DIR / project_name
    return project_path

def get_file_path(project_name: str, file_name: str) -> Path:
    """Get the full path to a file within a project."""
    return get_project_path(project_name) / file_name

def format_timestamp(timestamp: float) -> str:
    """Format a timestamp as ISO 8601 string."""
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

def create_backup():
    """Create a backup of all data."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"backup_{timestamp}"
    logger.info(f"Creating backup: {backup_path}")
    
    try:
        # Create a snapshot of all projects except the backups folder
        projects = [p for p in DATA_DIR.iterdir() if p.is_dir() and p.name != "backups"]
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for project in projects:
            dst = backup_path / project.name
            shutil.copytree(project, dst)
        
        # Cleanup old backups (keep last 5)
        backups = sorted(BACKUP_DIR.iterdir(), key=lambda p: p.stat().st_mtime)
        for old_backup in backups[:-5]:
            if old_backup.is_dir():
                shutil.rmtree(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
        
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

# API routes

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "Memory Storage MCP is running", "version": "1.0.0"}

@app.get("/projects", response_model=List[ProjectInfo])
async def list_projects(_: bool = Depends(verify_auth)):
    """List all projects."""
    try:
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
        project_path = get_project_path(project.name)
        if project_path.exists():
            raise HTTPException(status_code=400, detail=f"Project '{project.name}' already exists")
        
        project_path.mkdir(parents=True, exist_ok=True)
        return {"status": "success", "message": f"Project '{project.name}' created"}
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

# Background task for periodic backups
async def run_periodic_backups():
    """Run periodic backup tasks."""
    logger.info(f"Starting periodic backup scheduler (interval: {BACKUP_INTERVAL} minutes)")
    
    schedule.every(BACKUP_INTERVAL).minutes.do(create_backup)
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Check every minute

@app.on_event("startup")
async def startup_event():
    """Execute actions on application startup."""
    logger.info(f"Memory Storage MCP starting on port {PORT}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Authentication: {'Enabled' if AUTH_ENABLED else 'Disabled'}")
    
    # Create initial backup
    create_backup()
    
    # Start backup scheduler
    asyncio.create_task(run_periodic_backups())

# Main entrypoint
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False) 