"""Utility interface router (UG-ISP Router).

Provides utility functions for file operations, datetime, and formatting.
NO debug/logging calls - pure utility implementation.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List


# File operations (Local Network implementation)
def _read_file(file_path: str) -> str:
    """Read file contents.

    Args:
        file_path: Path to file

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file not found
        IOError: If file cannot be read
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _write_file(file_path: str, content: str) -> None:
    """Write content to file.

    Args:
        file_path: Path to file
        content: Content to write

    Raises:
        IOError: If file cannot be written
    """
    # Create parent directories if needed
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _list_files(directory: str, pattern: str = '*') -> List[str]:
    """List files in directory.

    Args:
        directory: Directory path
        pattern: Glob pattern (default: *)

    Returns:
        List of file paths
    """
    path = Path(directory)
    return [str(f) for f in path.rglob(pattern) if f.is_file()]


def _ensure_directory(directory: str) -> None:
    """Ensure directory exists.

    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


# DateTime utilities
def _get_timestamp() -> str:
    """Get current timestamp.

    Returns:
        Timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_date_string() -> str:
    """Get current date string.

    Returns:
        Date string (YYYY-MM-DD)
    """
    return datetime.now().strftime('%Y-%m-%d')


def _generate_scan_id() -> str:
    """Generate unique scan ID.

    Returns:
        Scan ID (YYYY-MM-DD_NNN format)
    """
    date_str = _get_date_string()
    # This is a placeholder - actual run number should come from report directory
    return f"{date_str}_001"


# Formatting utilities
def _format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON string.

    Args:
        data: Data to format
        indent: Indentation spaces

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def _parse_json(json_str: str) -> Any:
    """Parse JSON string.

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed data

    Raises:
        json.JSONDecodeError: If invalid JSON
    """
    return json.loads(json_str)


def _format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as markdown table.

    Args:
        headers: Table headers
        rows: Table rows (list of lists)

    Returns:
        Markdown table string
    """
    if not rows:
        return '| ' + ' | '.join(headers) + ' |\n'

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Build table
    lines = []

    # Header row
    header_cells = [str(h).ljust(w) for h, w in zip(headers, col_widths)]
    lines.append('| ' + ' | '.join(header_cells) + ' |')

    # Separator row
    sep_cells = ['-' * w for w in col_widths]
    lines.append('| ' + ' | '.join(sep_cells) + ' |')

    # Data rows
    for row in rows:
        cells = [str(row[i]).ljust(col_widths[i]) if i < len(row) else ''.ljust(col_widths[i])
                 for i in range(len(col_widths))]
        lines.append('| ' + ' | '.join(cells) + ' |')

    return '\n'.join(lines)


# Dispatch dictionary - O(1) operation routing
_UTILITY_DISPATCH = {
    # File operations
    'read_file': lambda **kw: _read_file(kw.get('file_path')),
    'write_file': lambda **kw: _write_file(kw.get('file_path'), kw.get('content')),
    'list_files': lambda **kw: _list_files(kw.get('directory'), kw.get('pattern', '*')),
    'ensure_directory': lambda **kw: _ensure_directory(kw.get('directory')),

    # DateTime utilities
    'get_timestamp': lambda **kw: _get_timestamp(),
    'get_date_string': lambda **kw: _get_date_string(),
    'generate_scan_id': lambda **kw: _generate_scan_id(),

    # Formatting utilities
    'format_json': lambda **kw: _format_json(kw.get('data'), kw.get('indent', 2)),
    'parse_json': lambda **kw: _parse_json(kw.get('json_str')),
    'format_markdown_table': lambda **kw: _format_markdown_table(
        kw.get('headers', []),
        kw.get('rows', [])
    ),
}


def execute_utility_operation(operation: str, **kwargs) -> Any:
    """Route utility operation requests to implementation functions.

    UG-ISP: This is the Router's execute operation function, called by
    the Gateway (ISP) to route operations to the Local Network (implementation).

    Args:
        operation: The utility operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown

    Example:
        # Called by Gateway via execute_operation()
        content = execute_utility_operation('read_file', file_path='test.py')
    """
    if operation not in _UTILITY_DISPATCH:
        raise ValueError(
            f"Unknown utility operation: '{operation}'. "
            f"Valid: {', '.join(_UTILITY_DISPATCH.keys())}"
        )

    # Execute operation through dispatch handler (O(1) lookup)
    handler = _UTILITY_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_utility_operation']
