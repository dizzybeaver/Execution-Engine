"""Utility Factory - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Factory contains all business logic for utility operations
Type: EE 2.1 Factory Implementation
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List
from pathlib import Path
from datetime import datetime
import json


class UtilityFactory:
    """Factory for utility operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all business logic for file operations, datetime, and formatting
    - Use DI (logger, metrics, config, call_operation)
    - NO interface logic
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize Utility Factory with DI.

        Args:
            get_logger: Logger getter function
            get_metrics: Metrics getter function
            get_config: Config getter function
            call_operation: Operation caller function
        """
        self.logger = get_logger("scanner.utility.factory")
        self.metrics = get_metrics("scanner.utility.factory")
        self._call_operation = call_operation
        self._get_config = get_config

    # File operations

    def read_file(self, file_path: str) -> str:
        """Read file contents.

        Args:
            file_path: Path to file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file not found
            IOError: If file cannot be read
        """
        self.logger.debug(f"Reading file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.metrics.increment('utility.read_file.calls', value=1)
        return content

    def write_file(self, file_path: str, content: str) -> None:
        """Write content to file.

        Args:
            file_path: Path to file
            content: Content to write

        Raises:
            IOError: If file cannot be written
        """
        self.logger.debug(f"Writing file: {file_path}")
        # Create parent directories if needed
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.metrics.increment('utility.write_file.calls', value=1)

    def list_files(self, directory: str, pattern: str = '*') -> List[str]:
        """List files in directory.

        Args:
            directory: Directory path
            pattern: Glob pattern (default: *)

        Returns:
            List of file paths
        """
        self.logger.debug(f"Listing files in {directory} with pattern {pattern}")
        path = Path(directory)
        files = [str(f) for f in path.rglob(pattern) if f.is_file()]
        self.metrics.increment('utility.list_files.calls', value=1)
        return files

    def ensure_directory(self, directory: str) -> None:
        """Ensure directory exists.

        Args:
            directory: Directory path
        """
        self.logger.debug(f"Ensuring directory exists: {directory}")
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.metrics.increment('utility.ensure_directory.calls', value=1)

    # DateTime utilities

    def get_timestamp(self) -> str:
        """Get current timestamp.

        Returns:
            Timestamp string (YYYY-MM-DD HH:MM:SS)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logger.debug(f"Generated timestamp: {timestamp}")
        return timestamp

    def get_date_string(self) -> str:
        """Get current date string.

        Returns:
            Date string (YYYY-MM-DD)
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.logger.debug(f"Generated date string: {date_str}")
        return date_str

    def generate_scan_id(self) -> str:
        """Generate unique scan ID.

        Returns:
            Scan ID (YYYY-MM-DD_NNN format)

        Note:
            This is a placeholder - actual run number should come from report directory
        """
        date_str = self.get_date_string()
        # This is a placeholder - actual run number should come from report directory
        scan_id = f"{date_str}_001"
        self.logger.debug(f"Generated scan ID: {scan_id}")
        return scan_id

    # Formatting utilities

    def format_json(self, data: Any, indent: int = 2) -> str:
        """Format data as JSON string.

        Args:
            data: Data to format
            indent: Indentation spaces

        Returns:
            Formatted JSON string
        """
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)
        self.logger.debug("Formatted data as JSON")
        self.metrics.increment('utility.format_json.calls', value=1)
        return json_str

    def parse_json(self, json_str: str) -> Any:
        """Parse JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            Parsed data

        Raises:
            json.JSONDecodeError: If invalid JSON
        """
        self.logger.debug("Parsing JSON string")
        self.metrics.increment('utility.parse_json.calls', value=1)
        return json.loads(json_str)

    def format_markdown_table(
        self,
        headers: List[str],
        rows: List[List[str]]
    ) -> str:
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
            cells = [
                str(row[i]).ljust(col_widths[i]) if i < len(row) else ''.ljust(col_widths[i])
                for i in range(len(col_widths))
            ]
            lines.append('| ' + ' | '.join(cells) + ' |')

        table = '\n'.join(lines)
        self.logger.debug(f"Formatted markdown table with {len(rows)} rows")
        self.metrics.increment('utility.format_markdown_table.calls', value=1)
        return table


__all__ = ['UtilityFactory']
