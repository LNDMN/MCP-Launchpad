# Этот файл будет адаптирован и, возможно, переименован 
# в mcp_text_editor_launchpad_adapter/__init__.py
"""MCP Text Editor Server package."""

import asyncio

from .server import main
from .text_editor import TextEditor

# Create a global text editor instance
_text_editor = TextEditor()


def run() -> None:
    """Run the MCP Text Editor Server."""
    asyncio.run(main())

__all__ = ["run", "TextEditor", "_text_editor"] # Добавила TextEditor и _text_editor в __all__ для возможного импорта 