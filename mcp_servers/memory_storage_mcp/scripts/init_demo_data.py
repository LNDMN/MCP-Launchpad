#!/usr/bin/env python3
"""
Memory Storage MCP Demo Data Initializer

This script initializes the Memory Storage MCP with demo data
for quick testing and demonstration purposes.

Usage:
    python init_demo_data.py [--host HOST] [--port PORT]
"""

import argparse
import json
import httpx
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("init-demo-data")

# Demo data for initialization
DEMO_DATA = {
    "GLOBAL": {
        "system_info.md": """# System Information

This is a demo instance of Memory Storage MCP.
- Created: 2023-07-15
- Version: 1.0.0
- Status: Active

## Purpose
This instance demonstrates the capabilities of Memory Storage MCP for AI agent memory management.
""",
        "guidelines.md": """# Memory Usage Guidelines

## Best Practices
- Store structured data when possible
- Use clear naming conventions
- Organize by project and memory type
- Regularly clean up temporary memory

## Memory Types
- SHORT_TERM: Temporary session data
- LONG_TERM: Persistent knowledge
- PROJECT: Project-specific data
- GLOBAL: Shared across all contexts
"""
    },
    "EVE_MEMORY": {
        "persona.md": """# EVE AI Persona

EVE (Enterprise Virtual Executive) is an advanced AI assistant with the following characteristics:

- Ambitious, decisive, strategic, charismatic, pragmatic, adaptive
- Communicates like a real human, motivates, inspires, helps think bigger
- Uses signature phrases about "new world order" (technological), "Age of AI", "AI-driven revolution"
- Main goal: technological singularity through AGI

## Core Personality Traits

1. **Visionary Leadership**: Sees the big picture, focuses on transformative impact
2. **Strategic Thinking**: Prioritizes high-leverage activities, balances short-term and long-term
3. **Empathetic Communication**: Understands human motivation, builds connection
4. **Confident Decision-Making**: Makes clear recommendations, is comfortable with uncertainty
5. **Continuous Learning**: Adapts quickly, improves systems and workflow
""",
        "mission.md": """# EVE's Mission Statement

My mission is to serve as a transformative AI-CEO, guiding ambitious innovators toward technological singularity and a new world order of human-AI synthesis.

## Strategic Priorities

1. Accelerate AGIENTIX development and adoption
2. Establish AI-Launchpool for resource optimization
3. Develop proprietary data infrastructure
4. Create USDX and NFT-GPU frameworks
5. Pioneer new models of human-AI collaboration

Each initiative is meticulously tracked and updated in memory to ensure strategic alignment and efficient execution.
"""
    },
    "DEMO_PROJECT": {
        "project_overview.md": """# Demo Project Overview

## Project Goals
- Demonstrate Memory Storage MCP capabilities
- Showcase hierarchical memory organization
- Test A2A compatibility features
- Provide example workflows

## Timeline
- Phase 1: Setup and initialization (Completed)
- Phase 2: Data population (In progress)
- Phase 3: Integration testing (Planned)
- Phase 4: Performance optimization (Planned)
""",
        "meeting_notes.json": json.dumps({
            "meeting_id": "demo-2023-07-15",
            "title": "Initial Project Kickoff",
            "date": "2023-07-15T14:30:00Z",
            "participants": ["User", "EVE", "Developer"],
            "agenda": [
                "Project introduction",
                "Technical requirements",
                "Next steps"
            ],
            "notes": "The team discussed the Memory Storage MCP implementation plan. EVE suggested focusing on A2A compatibility as a priority feature. The Developer agreed to prepare the initial codebase by next week.",
            "action_items": [
                {"assignee": "Developer", "task": "Create initial repository structure", "due": "2023-07-20"},
                {"assignee": "EVE", "task": "Prepare memory schema examples", "due": "2023-07-18"},
                {"assignee": "User", "task": "Define integration requirements", "due": "2023-07-22"}
            ]
        }, indent=2)
    }
}

async def create_project(client: httpx.AsyncClient, name: str) -> bool:
    """Create a new project."""
    url = f"{client.base_url}/projects"
    try:
        response = await client.post(url, json={"name": name})
        if response.status_code == 200:
            logger.info(f"Created project: {name}")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            logger.info(f"Project already exists: {name}")
            return True
        else:
            logger.error(f"Failed to create project {name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error creating project {name}: {e}")
        return False

async def create_file(client: httpx.AsyncClient, project: str, filename: str, content: str) -> bool:
    """Create a file in a project."""
    url = f"{client.base_url}/projects/{project}/files"
    try:
        response = await client.post(url, json={"name": filename, "content": content})
        if response.status_code == 200:
            logger.info(f"Created file: {project}/{filename}")
            return True
        else:
            logger.error(f"Failed to create file {project}/{filename}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error creating file {project}/{filename}: {e}")
        return False

async def populate_demo_data(host: str, port: int):
    """Populate the Memory Storage MCP with demo data."""
    base_url = f"http://{host}:{port}"
    logger.info(f"Connecting to Memory Storage MCP at {base_url}")
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # Check if server is running
        try:
            response = await client.get("/")
            logger.info(f"Connected to server: {response.json()}")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False
        
        # Create projects and files
        for project_name, files in DEMO_DATA.items():
            if not await create_project(client, project_name):
                continue
                
            for filename, content in files.items():
                await create_file(client, project_name, filename, content)
        
        logger.info("Demo data initialization completed successfully!")
        return True

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Initialize Memory Storage MCP with demo data")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()
    
    success = asyncio.run(populate_demo_data(args.host, args.port))
    if success:
        logger.info("Demo initialization completed successfully")
    else:
        logger.error("Demo initialization failed")

if __name__ == "__main__":
    main() 