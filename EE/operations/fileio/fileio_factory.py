"""
FileIO Factory - Operations Domain

File I/O operations implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

import os
import logging
from typing import Any, Dict, Optional, Callable, Union


class FileIOFactory:
    """File I/O operations factory.

    Provides safe file operations with error handling.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize file I/O factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

    def read(
        self,
        path: str,
        mode: str = "r",
        encoding: str = "utf-8",
        **kwargs
    ) -> Optional[Union[str, bytes]]:
        """Read file content.

        Args:
            path: File path
            mode: Read mode ('r' for text, 'rb' for binary)
            encoding: Text encoding (for text mode)
            **kwargs: Additional parameters

        Returns:
            File content or None if error
        """
        try:
            with open(path, mode, encoding=encoding if 'b' not in mode else None) as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"File not found: {path}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading file {path}: {e}")
            return None

    def write(
        self,
        path: str,
        content: Union[str, bytes],
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs
    ) -> bool:
        """Write content to file.

        Args:
            path: File path
            content: Content to write
            mode: Write mode ('w' for text, 'wb' for binary)
            encoding: Text encoding (for text mode)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, mode, encoding=encoding if 'b' not in mode else None) as f:
                f.write(content)
            return True
        except Exception as e:
            self.logger.error(f"Error writing file {path}: {e}")
            return False

    def append(
        self,
        path: str,
        content: Union[str, bytes],
        mode: str = "a",
        encoding: str = "utf-8",
        **kwargs
    ) -> bool:
        """Append content to file.

        Args:
            path: File path
            content: Content to append
            mode: Append mode ('a' for text, 'ab' for binary)
            encoding: Text encoding (for text mode)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, mode, encoding=encoding if 'b' not in mode else None) as f:
                f.write(content)
            return True
        except Exception as e:
            self.logger.error(f"Error appending to file {path}: {e}")
            return False

    def delete(self, path: str, **kwargs) -> bool:
        """Delete file.

        Args:
            path: File path
            **kwargs: Additional parameters

        Returns:
            True if deleted or doesn't exist
        """
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting file {path}: {e}")
            return False

    def exists(self, path: str, **kwargs) -> bool:
        """Check if file exists.

        Args:
            path: File path
            **kwargs: Additional parameters

        Returns:
            True if file exists
        """
        return os.path.exists(path)


__all__ = [
    "FileIOFactory",
]
