#!/usr/bin/env python3
"""
Memory Storage MCP - Configuration Tests

This module tests the configuration loading and settings of Memory Storage MCP.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest
import yaml

# Add parent directory to path to import app
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import config functions
from app import load_config, get_config, DEFAULT_CONFIG

@pytest.fixture
def temp_config_file() -> Generator[Path, None, None]:
    """Create a temporary config file for testing."""
    temp_file = Path(tempfile.mktemp(suffix=".yaml"))
    yield temp_file
    if temp_file.exists():
        os.unlink(temp_file)

def write_config(config_file: Path, config: Dict[str, Any]) -> None:
    """Write a config dictionary to a YAML file."""
    with open(config_file, "w") as f:
        yaml.dump(config, f)

def test_default_config() -> None:
    """Test that default config has expected values."""
    # Check that DEFAULT_CONFIG has the expected structure
    assert "server" in DEFAULT_CONFIG
    assert "storage" in DEFAULT_CONFIG
    assert "security" in DEFAULT_CONFIG
    
    # Check server settings
    assert "host" in DEFAULT_CONFIG["server"]
    assert "port" in DEFAULT_CONFIG["server"]
    assert "debug" in DEFAULT_CONFIG["server"]
    
    # Check storage settings
    assert "data_dir" in DEFAULT_CONFIG["storage"]
    assert "backup_dir" in DEFAULT_CONFIG["storage"]
    
    # Check security settings
    assert "enable_auth" in DEFAULT_CONFIG["security"]
    assert "api_keys" in DEFAULT_CONFIG["security"]

def test_load_config_default() -> None:
    """Test loading default config when no file exists."""
    non_existent_file = Path("/tmp/non_existent_config.yaml")
    
    # Ensure file doesn't exist
    if non_existent_file.exists():
        os.unlink(non_existent_file)
    
    # Load config with non-existent file
    config = load_config(non_existent_file)
    
    # Should return the default config
    assert config == DEFAULT_CONFIG

def test_load_config_file(temp_config_file: Path) -> None:
    """Test loading config from file."""
    # Create custom config
    custom_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 9000,
            "debug": True
        },
        "storage": {
            "data_dir": "/custom/data/path",
            "backup_dir": "/custom/backup/path"
        },
        "security": {
            "enable_auth": True,
            "api_keys": ["test_key_1", "test_key_2"]
        }
    }
    
    # Write custom config to file
    write_config(temp_config_file, custom_config)
    
    # Load config from file
    config = load_config(temp_config_file)
    
    # Should match custom config
    assert config == custom_config

def test_load_config_partial(temp_config_file: Path) -> None:
    """Test loading partial config, should merge with defaults."""
    # Create partial config
    partial_config = {
        "server": {
            "port": 9000
        },
        "security": {
            "enable_auth": True
        }
    }
    
    # Write partial config to file
    write_config(temp_config_file, partial_config)
    
    # Load config from file
    config = load_config(temp_config_file)
    
    # Should merge with defaults
    expected = DEFAULT_CONFIG.copy()
    expected["server"]["port"] = 9000
    expected["security"]["enable_auth"] = True
    
    assert config["server"]["port"] == 9000
    assert config["security"]["enable_auth"] is True
    assert config["server"]["host"] == DEFAULT_CONFIG["server"]["host"]
    assert config["storage"]["data_dir"] == DEFAULT_CONFIG["storage"]["data_dir"]

def test_get_config_environment_override() -> None:
    """Test environment variables overriding config."""
    # Set environment variables
    os.environ["MEMORY_STORAGE_SERVER_PORT"] = "8888"
    os.environ["MEMORY_STORAGE_DATA_DIR"] = "/env/data/path"
    os.environ["MEMORY_STORAGE_ENABLE_AUTH"] = "true"
    
    # Get config (should use defaults + env vars)
    config = get_config()
    
    # Check that env vars override defaults
    assert config["server"]["port"] == 8888
    assert config["storage"]["data_dir"] == "/env/data/path"
    assert config["security"]["enable_auth"] is True
    
    # Clean up environment
    del os.environ["MEMORY_STORAGE_SERVER_PORT"]
    del os.environ["MEMORY_STORAGE_DATA_DIR"]
    del os.environ["MEMORY_STORAGE_ENABLE_AUTH"]

def test_config_types() -> None:
    """Test that config values have the correct types."""
    os.environ["MEMORY_STORAGE_SERVER_PORT"] = "8888"
    os.environ["MEMORY_STORAGE_SERVER_DEBUG"] = "true"
    
    config = get_config()
    
    # Verify types are correctly parsed
    assert isinstance(config["server"]["port"], int)
    assert isinstance(config["server"]["debug"], bool)
    
    # Clean up environment
    del os.environ["MEMORY_STORAGE_SERVER_PORT"]
    del os.environ["MEMORY_STORAGE_SERVER_DEBUG"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 