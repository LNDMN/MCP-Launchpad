"""Core text editor functionality with file operation handling."""

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from mcp_text_editor_launchpad_adapter.models import (
    DeleteTextFileContentsRequest,
    EditPatch,
    FileRange,
    FileRanges,
    EditResult,
    EditFileOperation
)
from mcp_text_editor_launchpad_adapter.service import TextEditorService

logger = logging.getLogger(__name__)


class TextEditor:
    """Handles text file operations with security checks and conflict detection."""

    def __init__(self):
        """Initialize TextEditor."""
        self._validate_environment()
        self.service = TextEditorService()

    def create_error_response(
        self,
        error_message: str,
        content_hash: Optional[str] = None,
        file_path: Optional[str] = None,
        suggestion: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a standardized error response.

        Args:
            error_message (str): The error message to include
            content_hash (Optional[str], optional): Hash of the current content if available
            file_path (Optional[str], optional): File path to use as dictionary key
            suggestion (Optional[str], optional): Suggested operation type
            hint (Optional[str], optional): Hint message for users

        Returns:
            Dict[str, Any]: Standardized error response structure
        """
        error_response = {
            "result": "error",
            "reason": error_message,
            "file_hash": content_hash,
        }

        # Add fields if provided
        if content_hash is not None:
            error_response["file_hash"] = content_hash
        if suggestion:
            error_response["suggestion"] = suggestion
        if hint:
            error_response["hint"] = hint

        if file_path:
            return {file_path: error_response}
        return error_response

    def _validate_environment(self) -> None:
        """
        Validate environment variables and setup.
        Can be extended to check for specific permissions or configurations.
        """
        # Future: Add environment validation if needed
        pass  # pragma: no cover

    def _validate_file_path(self, file_path: str | os.PathLike) -> None:
        """
        Validate if file path is allowed and secure.

        Args:
            file_path (str | os.PathLike): Path to validate

        Raises:
            ValueError: If path is not allowed or contains dangerous patterns
        """
        # Convert path to string for checking
        path_str = str(file_path)

        # Check for dangerous patterns
        if ".." in path_str:
            raise ValueError("Path traversal not allowed")

    @staticmethod
    def calculate_hash(content: str) -> str:
        """
        Calculate SHA-256 hash of content.

        Args:
            content (str): Content to hash

        Returns:
            str: Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()

    async def _read_file(
        self, file_path: str, encoding: str = "utf-8"
    ) -> Tuple[List[str], str, int]:
        """Read file and return lines, content, and total lines.

        Args:
            file_path (str): Path to the file to read
            encoding (str, optional): File encoding. Defaults to "utf-8"

        Returns:
            Tuple[List[str], str, int]: Lines, content, and total line count

        Raises:
            FileNotFoundError: If file not found
            UnicodeDecodeError: If file cannot be decoded with specified encoding
        """
        self._validate_file_path(file_path)
        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
            file_content = "".join(lines)
            return lines, file_content, len(lines)
        except FileNotFoundError as err:
            raise FileNotFoundError(f"File not found: {file_path}") from err
        except UnicodeDecodeError as err:
            raise UnicodeDecodeError(
                encoding,
                err.object,
                err.start,
                err.end,
                f"Failed to decode file '{file_path}' with {encoding} encoding",
            ) from err

    async def read_multiple_ranges(
        self, ranges: List[Dict[str, Any]], encoding: str = "utf-8"
    ) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}

        for file_range_dict in ranges:
            file_range = FileRanges.model_validate(file_range_dict)
            file_path = file_range.file_path
            lines, file_content, total_lines = await self._read_file(
                file_path, encoding=encoding
            )
            file_hash = self.calculate_hash(file_content)
            result[file_path] = {"ranges": [], "file_hash": file_hash}

            for range_spec in file_range.ranges:
                start = max(1, range_spec.start) - 1
                end_value = range_spec.end
                end = (
                    min(total_lines, end_value)
                    if end_value is not None
                    else total_lines
                )

                if start >= total_lines:
                    empty_content = ""
                    result[file_path]["ranges"].append(
                        {
                            "content": empty_content,
                            "start": start + 1,
                            "end": start + 1,
                            "range_hash": self.calculate_hash(empty_content),
                            "total_lines": total_lines,
                            "content_size": 0,
                        }
                    )
                    continue

                selected_lines = lines[start:end]
                content = "".join(selected_lines)
                range_hash = self.calculate_hash(content)

                result[file_path]["ranges"].append(
                    {
                        "content": content,
                        "start": start + 1,
                        "end": end,
                        "range_hash": range_hash,
                        "total_lines": total_lines,
                        "content_size": len(content),
                    }
                )

        return result

    async def read_file_contents(
        self,
        file_path: str,
        start: int = 1,
        end: Optional[int] = None,
        encoding: str = "utf-8",
    ) -> Tuple[str, int, int, str, int, int]:
        lines, file_content, total_lines = await self._read_file(
            file_path, encoding=encoding
        )

        if end is not None and end < start:
            raise ValueError("End line must be greater than or equal to start line")

        start = max(1, start) - 1
        end = total_lines if end is None else min(end, total_lines)

        if start >= total_lines:
            empty_content = ""
            empty_hash = self.calculate_hash(empty_content)
            return empty_content, start, start, empty_hash, total_lines, 0
        if end < start:
            raise ValueError("End line must be greater than or equal to start line")

        selected_lines = lines[start:end]
        content = "".join(selected_lines)
        content_hash = self.calculate_hash(content)
        content_size = len(content.encode(encoding))

        return (
            content,
            start + 1,
            end,
            content_hash,
            total_lines,
            content_size,
        )

    async def edit_file_contents(
        self,
        file_path: str,
        expected_file_hash: str,
        patches: List[Dict[str, Any]],
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """
        Edit file contents with hash-based conflict detection and multiple patches.

        Args:
            file_path (str): Path to the file to edit
            expected_file_hash (str): Expected hash of the file before editing
            patches (List[Dict[str, Any]]): List of patches to apply, each containing:
                - start (int): Starting line number (1-based)
                - end (Optional[int]): Ending line number (inclusive)
                - contents (str): New content to insert (if empty string, consider using delete_text_file_contents instead)
                - range_hash (str): Expected hash of the content being replaced

        Returns:
            Dict[str, Any]: Results of the operation containing:
                - result: "ok" or "error"
                - hash: New file hash if successful, None if error
                - reason: Error message if result is "error"
        """
        self._validate_file_path(file_path)
        try:
            # Initialize lines and current_file_hash for all paths
            lines: List[str] = []
            current_file_hash: Optional[str] = None
            current_file_content: str = ""

            if not os.path.exists(file_path):
                if expected_file_hash not in ["", None]:  # Allow null hash for new files
                    return self.create_error_response(
                        "File not found and non-empty hash provided",
                        suggestion="append", # Or create_text_file
                        hint="For new files, ensure hash is empty or use create/append tools.",
                        file_path=file_path
                    )
                parent_dir = os.path.dirname(file_path)
                if parent_dir:
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                    except OSError as e:
                        return self.create_error_response(
                            f"Failed to create directory: {str(e)}",
                            file_path=file_path
                        )
                current_file_hash = self.calculate_hash("") # Empty file hash
                lines = []
                current_file_content = ""
            else:
                read_lines, read_content, _ = await self._read_file(file_path, encoding)
                lines = read_lines
                current_file_content = read_content
                current_file_hash = self.calculate_hash(current_file_content)

            if current_file_hash != expected_file_hash:
                return self.create_error_response(
                    "File hash mismatch",
                    content_hash=current_file_hash,
                    file_path=file_path,
                    suggestion="get",
                    hint="Please use get_text_file_contents to get updated hash."
                )

            patch_objects = [EditPatch.model_validate(p) for p in patches]
            
            # Validate patches for overlaps and individual range_hash validity before applying
            # Sort by start line for overlap check, and original content validation
            temp_sorted_patches = sorted(patch_objects, key=lambda x: x.start)
            last_line_covered = 0
            for i, patch in enumerate(temp_sorted_patches):
                patch_start_idx = patch.start -1
                # Corrected patch_end_idx calculation for validation
                patch_end_idx = (patch.end -1) if patch.end is not None else (len(lines) -1 if lines else -1)

                if patch_start_idx < 0 or patch_start_idx > len(lines) or \
                   (patch.end is not None and (patch.end < patch.start or patch_end_idx >= len(lines) if lines else patch_end_idx > -1)):
                    return self.create_error_response(
                        f"Invalid line numbers in patch {i+1} (start: {patch.start}, end: {patch.end}). Total lines: {len(lines)}", 
                        content_hash=current_file_hash, file_path=file_path
                    )

                if patch_start_idx < last_line_covered: # Overlap check
                     return self.create_error_response(
                        "Overlapping patches detected", 
                        content_hash=current_file_hash, file_path=file_path
                    )
                last_line_covered = patch_end_idx +1 
                
                # Validate range_hash for non-insertion patches
                # An empty range_hash signifies an insertion
                if patch.range_hash != "": 
                    # Ensure lines exist to take a slice if it's not an insertion into an empty part
                    if patch_start_idx < len(lines):
                        actual_range_content = "".join(lines[patch_start_idx : patch_end_idx + 1])
                        calculated_range_hash = self.calculate_hash(actual_range_content)
                        if calculated_range_hash != patch.range_hash:
                            return self.create_error_response(
                                f"Range hash mismatch for patch {i+1} (lines {patch.start}-{patch.end}). Expected '{patch.range_hash}', got '{calculated_range_hash}'",
                                content_hash=current_file_hash,
                                file_path=file_path,
                                suggestion="get",
                                hint="Content of the specified range may have changed. Please get fresh content and hashes."
                            )
                    elif patch.range_hash: # If range_hash is provided but there are no lines to hash (e.g. insert at EOF of empty file)
                        return self.create_error_response(
                            f"Range hash '{patch.range_hash}' provided for patch {i+1} but no content exists in specified range (lines {patch.start}-{patch.end}). For insertions, range_hash should be an empty string.",
                            content_hash=current_file_hash,
                            file_path=file_path,
                            suggestion="patch",
                            hint="Ensure range_hash is empty for pure insertions or verify line numbers."
                        )
            

            # Apply patches in reverse order of start line to manage index shifts correctly
            for patch in sorted(patch_objects, key=lambda p: p.start, reverse=True):
                start_idx = patch.start - 1 
                is_pure_insertion = patch.range_hash == ""

                # Determine end_idx for replacement or point of insertion
                if is_pure_insertion:
                    end_idx = start_idx # For insertion, we don't remove a range, so end is effectively start
                else:
                    end_idx = (patch.end -1 if patch.end is not None else len(lines)-1)
                
                patch_content_lines = patch.contents.splitlines(keepends=True)
                # Ensure last line of patch content has a newline, unless it's totally empty content
                if patch.contents and not patch.contents.endswith('\n'):
                    if patch_content_lines: # If there are any lines (i.e. content is not just whitespace)
                        patch_content_lines[-1] += '\n'
                    else: # Content is non-empty but has no newlines (e.g. "abc")
                        patch_content_lines = [patch.contents + '\n']
                elif not patch_content_lines and patch.contents == "": # Explicitly empty content string
                    patch_content_lines = []
                
                if is_pure_insertion:
                    lines[start_idx:start_idx] = patch_content_lines
                else:
                    lines[start_idx : end_idx + 1] = patch_content_lines

            final_content = "".join(lines)
            with open(file_path, "w", encoding=encoding) as f:
                f.write(final_content)

            new_hash = self.calculate_hash(final_content)
            return {
                file_path: EditResult(
                    result="ok", 
                    hash=new_hash, 
                    reason=None
                ).to_dict() # Use .to_dict() here
            }

        except FileNotFoundError:
            return {file_path: self.create_error_response(f"File not found: {file_path}").get(file_path)}
        except (IOError, UnicodeError, PermissionError) as e:
            logger.error(f"IO/Unicode/Permission error editing {file_path}: {str(e)}")
            return {file_path: self.create_error_response(f"Error editing file: {str(e)}").get(file_path)}
        except Exception as e:
            logger.error(f"Unexpected error editing {file_path}: {str(e)}\n{traceback.format_exc()}")
            return {file_path: self.create_error_response(f"Unexpected error: {str(e)}").get(file_path)}

    async def insert_text_file_contents(
        self,
        file_path: str,
        file_hash: str,
        contents: str,
        after: Optional[int] = None,
        before: Optional[int] = None,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Insert text content before or after a specific line in a file.

        Args:
            file_path (str): Path to the file to edit
            file_hash (str): Expected hash of the file before editing
            contents (str): Content to insert
            after (Optional[int]): Line number after which to insert content
            before (Optional[int]): Line number before which to insert content
            encoding (str, optional): File encoding. Defaults to "utf-8"

        Returns:
            Dict[str, Any]: Results containing:
                - result: "ok" or "error"
                - hash: New file hash if successful
                - reason: Error message if result is "error"
        """
        self._validate_file_path(file_path)
        if (after is None and before is None) or (
            after is not None and before is not None
        ):
            return self.create_error_response("Exactly one of 'after' or 'before' must be specified", file_path=file_path)

        try:
            (
                current_content,
                _,
                _,
                current_hash,
                total_lines,
                _,
            ) = await self.read_file_contents(
                file_path,
                encoding=encoding,
            )

            if current_hash != file_hash:
                 return self.create_error_response(
                    "File hash mismatch", 
                    content_hash=current_hash, 
                    file_path=file_path,
                    suggestion="get",
                    hint="Use get_text_file_contents to get updated hash."
                )

            lines = current_content.splitlines(keepends=True)
            insert_pos: int
            if after is not None:
                if not (0 <= after <= total_lines):
                    return self.create_error_response(
                        f"Line number {after} for 'after' is out of bounds (0-{total_lines})",
                        content_hash=current_hash, file_path=file_path
                    )
                insert_pos = after
            elif before is not None: # before must be set
                if not (1 <= before <= total_lines + 1):
                    return self.create_error_response(
                        f"Line number {before} for 'before' is out of bounds (1-{total_lines + 1})",
                        content_hash=current_hash, file_path=file_path
                    )
                insert_pos = before - 1
            else:
                # This case should be caught by the initial validation
                return self.create_error_response("Insertion point not specified", file_path=file_path) 

            if not contents.endswith("\n") and contents != "":
                contents += "\n"
            
            # Handle insertion at the very beginning or very end if lines is empty
            if not lines and insert_pos == 0:
                lines = [contents]
            else:
                lines.insert(insert_pos, contents)

            final_content = "".join(lines)
            with open(file_path, "w", encoding=encoding) as f:
                f.write(final_content)

            new_hash = self.calculate_hash(final_content)
            return {file_path: EditResult(result="ok", hash=new_hash, reason=None).to_dict()}

        except FileNotFoundError:
            # If file not found, and we intend to insert (e.g. before=1 or after=0 on an empty/new file concept)
            # This could be treated as a file creation if file_hash is empty, indicating a new file.
            if file_hash == self.calculate_hash(""):
                parent_dir = os.path.dirname(file_path)
                if parent_dir:
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                    except OSError as e:
                        return self.create_error_response(f"Failed to create directory: {str(e)}", file_path=file_path)
                
                if not contents.endswith("\n") and contents != "":
                    contents += "\n"
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(contents)
                new_hash = self.calculate_hash(contents)
                return {file_path: EditResult(result="ok", hash=new_hash, reason=None).to_dict()}
            else:
                return self.create_error_response(f"File not found: {file_path}", file_path=file_path)
        except Exception as e:
            logger.error(f"Error inserting text into {file_path}: {str(e)}\n{traceback.format_exc()}")
            return self.create_error_response(f"Error inserting text: {str(e)}", file_path=file_path)

    async def delete_text_file_contents(
        self,
        request: DeleteTextFileContentsRequest,
    ) -> Dict[str, Any]:
        """Delete specified ranges from a text file with conflict detection.

        Args:
            request (DeleteTextFileContentsRequest): The request containing:
                - file_path: Path to the text file
                - file_hash: Expected hash of the file before editing
                - ranges: List of ranges to delete
                - encoding: Optional text encoding (default: utf-8)

        Returns:
            Dict[str, Any]: Results containing:
                - result: "ok" or "error"
                - hash: New file hash if successful
                - reason: Error message if result is "error"
        """
        self._validate_file_path(request.file_path)
        file_path = request.file_path
        encoding = request.encoding or "utf-8"

        try:
            (
                current_content,
                _,
                _,
                current_hash,
                total_lines,
                _,
            ) = await self.read_file_contents(
                file_path,
                encoding=encoding,
            )

            if current_hash != request.file_hash:
                return self.create_error_response(
                    "File hash mismatch", 
                    content_hash=current_hash, 
                    file_path=file_path,
                    suggestion="get",
                    hint="Use get_text_file_contents to get updated hash."
                ) 

            lines = current_content.splitlines(keepends=True)

            if not request.ranges:
                return self.create_error_response(
                    "Missing required argument: ranges", 
                    content_hash=current_hash, 
                    file_path=file_path
                )

            if not self.service.validate_ranges(request.ranges, len(lines)):
                return self.create_error_response(
                    "Invalid ranges (overlap, out of bounds, or end before start)", 
                    content_hash=current_hash, 
                    file_path=file_path
                )
            
            # Create a set of line indices to remove for efficient deletion
            indices_to_remove = set()
            for range_to_delete in request.ranges:
                start_idx = range_to_delete.start - 1
                end_idx = (range_to_delete.end if range_to_delete.end is not None 
                           else total_lines) 
                
                # Validate range_hash before marking for deletion
                if range_to_delete.range_hash is not None and range_to_delete.range_hash != "":
                    content_to_delete = "".join(lines[start_idx:end_idx])
                    actual_range_hash = self.calculate_hash(content_to_delete)
                    if actual_range_hash != range_to_delete.range_hash:
                        return self.create_error_response(
                            f"Content hash mismatch for range {range_to_delete.start}-{range_to_delete.end}. Expected '{range_to_delete.range_hash}', got '{actual_range_hash}'",
                            content_hash=current_hash,
                            file_path=file_path,
                            suggestion="get",
                            hint="Content of the specified range may have changed. Please get fresh content and hashes."
                        )
                
                for i in range(start_idx, end_idx):
                    indices_to_remove.add(i)
            
            new_lines = [line for i, line in enumerate(lines) if i not in indices_to_remove]

            new_content = "".join(new_lines)
            with open(file_path, "w", encoding=encoding) as f:
                f.write(new_content)

            new_hash = self.calculate_hash(new_content)
            return {file_path: EditResult(result="ok", hash=new_hash, reason=None).to_dict()}

        except FileNotFoundError:
            return self.create_error_response(f"File not found: {file_path}", file_path=file_path)
        except Exception as e:
            logger.error(f"Error deleting contents for {file_path}: {str(e)}\n{traceback.format_exc()}")
            return self.create_error_response(f"Error deleting contents: {str(e)}", file_path=file_path) 