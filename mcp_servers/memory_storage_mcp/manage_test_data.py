#!/usr/bin/env python3
"""
Memory Storage MCP - Test Data Manager

This script manages test data for Memory Storage MCP.
It can create test fixtures, clear test data, and generate sample data for testing.
"""

import os
import sys
import json
import shutil
import random
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


class TestDataManager:
    """Test data manager for Memory Storage MCP."""
    
    def __init__(self, data_dir: Path):
        """
        Initialize the test data manager.
        
        Args:
            data_dir: Base directory for test data
        """
        self.data_dir = data_dir
        self.projects_dir = data_dir / "projects"
        self.backups_dir = data_dir / "backups"
    
    def setup_test_env(self) -> None:
        """Set up test environment directories."""
        # Create main directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        
        print(f"Test environment set up at {self.data_dir}")
    
    def clean_test_env(self) -> None:
        """Clean up test environment."""
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
            print(f"Test environment cleaned: {self.data_dir}")
        else:
            print(f"Test environment doesn't exist: {self.data_dir}")
    
    def generate_project(
        self, 
        project_name: str, 
        file_count: int = 5,
        with_content: bool = True
    ) -> None:
        """
        Generate a test project with random files.
        
        Args:
            project_name: Name of the project
            file_count: Number of files to generate
            with_content: Whether to add content to files
        """
        project_dir = self.projects_dir / project_name
        os.makedirs(project_dir, exist_ok=True)
        
        for i in range(file_count):
            file_type = random.choice(["md", "txt", "json", "yml"])
            file_name = f"test_file_{i+1}.{file_type}"
            file_path = project_dir / file_name
            
            if with_content:
                if file_type == "md":
                    content = self._generate_markdown()
                elif file_type == "json":
                    content = json.dumps(self._generate_json(), indent=2)
                elif file_type == "yml":
                    content = self._generate_yaml()
                else:
                    content = self._generate_text()
                
                with open(file_path, "w") as f:
                    f.write(content)
            else:
                # Create empty file
                file_path.touch()
        
        print(f"Generated project '{project_name}' with {file_count} files")
    
    def _generate_markdown(self) -> str:
        """Generate random markdown content."""
        headings = ["# Test Heading", "## Subheading", "### Details"]
        paragraphs = [
            "This is a test paragraph for testing purposes.",
            "Memory Storage MCP is a powerful tool for storing and managing data.",
            "Each project can contain multiple files with different content types."
        ]
        lists = [
            "- Item 1\n- Item 2\n- Item 3",
            "1. First\n2. Second\n3. Third"
        ]
        
        content_parts = []
        content_parts.append(random.choice(headings))
        content_parts.append("\n\n")
        content_parts.append(random.choice(paragraphs))
        content_parts.append("\n\n")
        content_parts.append(random.choice(lists))
        
        return "".join(content_parts)
    
    def _generate_json(self) -> Dict[str, Any]:
        """Generate random JSON content."""
        return {
            "name": f"test_object_{random.randint(1, 100)}",
            "created_at": datetime.datetime.now().isoformat(),
            "properties": {
                "type": random.choice(["document", "config", "data"]),
                "priority": random.randint(1, 5),
                "tags": random.sample(["test", "sample", "fixture", "demo", "example"], 
                                      k=random.randint(1, 3))
            },
            "status": random.choice(["active", "archived", "draft"])
        }
    
    def _generate_yaml(self) -> str:
        """Generate random YAML content."""
        return f"""# Test YAML file
version: {random.randint(1, 5)}.{random.randint(0, 9)}

config:
  name: test_config
  debug: {random.choice(["true", "false"])}
  port: {random.randint(3000, 9000)}
  
settings:
  - name: setting1
    value: {random.randint(10, 100)}
  - name: setting2
    value: {random.choice(["value1", "value2", "value3"])}
"""
    
    def _generate_text(self) -> str:
        """Generate random text content."""
        sentences = [
            "This is a test file.",
            "It contains random text for testing purposes.",
            "The content is generated automatically.",
            "Memory Storage MCP uses these files for testing.",
            "Each file has different content."
        ]
        
        num_paragraphs = random.randint(1, 3)
        paragraphs = []
        
        for _ in range(num_paragraphs):
            num_sentences = random.randint(2, 5)
            paragraph = " ".join(random.sample(sentences, k=min(num_sentences, len(sentences))))
            paragraphs.append(paragraph)
        
        return "\n\n".join(paragraphs)
    
    def generate_test_dataset(
        self, 
        project_count: int = 3, 
        max_files_per_project: int = 10
    ) -> None:
        """
        Generate a complete test dataset.
        
        Args:
            project_count: Number of projects to generate
            max_files_per_project: Maximum number of files per project
        """
        # Ensure test environment is set up
        self.setup_test_env()
        
        # Generate projects
        for i in range(project_count):
            project_name = f"test_project_{i+1}"
            file_count = random.randint(1, max_files_per_project)
            self.generate_project(project_name, file_count)
        
        print(f"Generated test dataset with {project_count} projects")
    
    def create_backup(self, backup_name: str, comment: str = "") -> None:
        """
        Create a backup of the current data.
        
        Args:
            backup_name: Name of the backup
            comment: Optional comment for the backup
        """
        from app import create_backup
        
        full_backup_name = create_backup(
            backup_name=backup_name,
            comment=comment,
            data_dir=self.projects_dir,
            backup_dir=self.backups_dir
        )
        
        print(f"Created backup: {full_backup_name}")


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage test data for Memory Storage MCP")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up test environment")
    setup_parser.add_argument("--data-dir", type=str, default="./test_data",
                              help="Base directory for test data")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean up test environment")
    clean_parser.add_argument("--data-dir", type=str, default="./test_data",
                              help="Base directory for test data")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate test data")
    generate_parser.add_argument("--data-dir", type=str, default="./test_data",
                                 help="Base directory for test data")
    generate_parser.add_argument("--projects", type=int, default=3,
                                 help="Number of projects to generate")
    generate_parser.add_argument("--files", type=int, default=5,
                                 help="Maximum number of files per project")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create a backup")
    backup_parser.add_argument("--data-dir", type=str, default="./test_data",
                               help="Base directory for test data")
    backup_parser.add_argument("--name", type=str, required=True,
                               help="Name of the backup")
    backup_parser.add_argument("--comment", type=str, default="",
                               help="Comment for the backup")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Convert data_dir to absolute path
    data_dir = Path(args.data_dir).absolute()
    manager = TestDataManager(data_dir)
    
    if args.command == "setup":
        manager.setup_test_env()
    elif args.command == "clean":
        manager.clean_test_env()
    elif args.command == "generate":
        manager.generate_test_dataset(args.projects, args.files)
    elif args.command == "backup":
        manager.create_backup(args.name, args.comment)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 