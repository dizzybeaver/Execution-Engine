"""Cleanup Factory - Scanner Domain (EE 2.1 Compliant).

Version: 2.1.0
Date: 2025-12-31
Purpose: Factory contains all business logic for scanner cleanup operations
Type: EE 2.1 Factory Implementation

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, get_config, call_operation via DI
- NO imports outside scanner domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

from __future__ import annotations
from typing import Any, Callable, Dict
from pathlib import Path


# =============================================================================
# Cleanup Factory Class
# =============================================================================

class CleanupFactory:
    """Factory for cleanup operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all cleanup business logic
    - Use DI (logger, metrics, config, call_operation)
    - Safe file system operations with error handling

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize cleanup factory with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        self.logger = get_logger("scanner.cleanup.factory")
        self.metrics = get_metrics("scanner.cleanup.factory")
        self._get_config = get_config
        self._call_operation = call_operation

    def cleanup_all(self, path: str = '.', **kwargs) -> Dict[str, Any]:
        """Clean all cache files and directories.

        Args:
            path: Path to clean (default: current directory)
            **kwargs: Additional parameters (unused)

        Returns:
            Cleanup result dict with success status, counts, and errors
        """
        clean_path = Path(path)
        pycache_dirs = 0
        pyc_files = 0
        pyo_files = 0
        errors = []

        # Remove __pycache__ directories
        for pycache in clean_path.rglob('__pycache__'):
            try:
                if pycache.is_dir():
                    # Count files before removing
                    file_count = len(list(pycache.iterdir()))
                    for item in pycache.iterdir():
                        item.unlink()
                    pycache.rmdir()
                    pycache_dirs += 1
                    pyc_files += file_count
                    self.logger.debug(f"Removed __pycache__: {pycache}")
            except Exception as e:
                error_msg = {
                    'path': str(pycache),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove __pycache__: {error_msg}")

        # Remove .pyc files (in case any remain outside __pycache__)
        for pyc_file in clean_path.rglob('*.pyc'):
            try:
                pyc_file.unlink()
                pyc_files += 1
                self.logger.debug(f"Removed .pyc file: {pyc_file}")
            except Exception as e:
                error_msg = {
                    'path': str(pyc_file),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove .pyc file: {error_msg}")

        # Remove .pyo files
        for pyo_file in clean_path.rglob('*.pyo'):
            try:
                pyo_file.unlink()
                pyo_files += 1
                self.logger.debug(f"Removed .pyo file: {pyo_file}")
            except Exception as e:
                error_msg = {
                    'path': str(pyo_file),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove .pyo file: {error_msg}")

        return {
            'success': len(errors) == 0,
            'pycache_dirs_removed': pycache_dirs,
            'pyc_files_removed': pyc_files,
            'pyo_files_removed': pyo_files,
            'total_items_removed': pycache_dirs + pyc_files + pyo_files,
            'errors': errors
        }

    def cleanup_pycache(self, path: str = '.', **kwargs) -> Dict[str, Any]:
        """Clean only __pycache__ directories.

        Args:
            path: Path to clean (default: current directory)
            **kwargs: Additional parameters (unused)

        Returns:
            Cleanup result dict with success status, counts, and errors
        """
        clean_path = Path(path)
        dirs_removed = 0
        files_removed = 0
        errors = []

        for pycache in clean_path.rglob('__pycache__'):
            try:
                if pycache.is_dir():
                    file_count = len(list(pycache.iterdir()))
                    for item in pycache.iterdir():
                        item.unlink()
                    pycache.rmdir()
                    dirs_removed += 1
                    files_removed += file_count
                    self.logger.debug(f"Removed __pycache__: {pycache}")
            except Exception as e:
                error_msg = {
                    'path': str(pycache),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove __pycache__: {error_msg}")

        return {
            'success': len(errors) == 0,
            'dirs_removed': dirs_removed,
            'files_removed': files_removed,
            'errors': errors
        }

    def cleanup_compiled(self, path: str = '.', **kwargs) -> Dict[str, Any]:
        """Clean only compiled files (.pyc, .pyo).

        Args:
            path: Path to clean (default: current directory)
            **kwargs: Additional parameters (unused)

        Returns:
            Cleanup result dict with success status, counts, and errors
        """
        clean_path = Path(path)
        pyc_count = 0
        pyo_count = 0
        errors = []

        for pyc_file in clean_path.rglob('*.pyc'):
            try:
                pyc_file.unlink()
                pyc_count += 1
                self.logger.debug(f"Removed .pyc file: {pyc_file}")
            except Exception as e:
                error_msg = {
                    'path': str(pyc_file),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove .pyc file: {error_msg}")

        for pyo_file in clean_path.rglob('*.pyo'):
            try:
                pyo_file.unlink()
                pyo_count += 1
                self.logger.debug(f"Removed .pyo file: {pyo_file}")
            except Exception as e:
                error_msg = {
                    'path': str(pyo_file),
                    'error': str(e)
                }
                errors.append(error_msg)
                self.logger.warning(f"Failed to remove .pyo file: {error_msg}")

        return {
            'success': len(errors) == 0,
            'pyc_files_removed': pyc_count,
            'pyo_files_removed': pyo_count,
            'total_files_removed': pyc_count + pyo_count,
            'errors': errors
        }


__all__ = ['CleanupFactory']
