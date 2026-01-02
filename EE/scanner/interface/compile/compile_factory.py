"""Compile Factory - EE 2.1 Compliant

Version: 2.1.0
Date: 2025-12-31
Purpose: Factory contains all business logic for compile operations
Type: EE 2.1 Factory Implementation
"""

from __future__ import annotations
from typing import Any, Callable, Dict
from pathlib import Path
import py_compile


class CompileFactory:
    """Factory for compile operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all business logic for Python compilation
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
        """Initialize Compile Factory with DI.

        Args:
            get_logger: Logger getter function
            get_metrics: Metrics getter function
            get_config: Config getter function
            call_operation: Operation caller function
        """
        self.logger = get_logger("scanner.compile.factory")
        self.metrics = get_metrics("scanner.compile.factory")
        self._call_operation = call_operation
        self._get_config = get_config

    def compile_all(self, path: str = '.') -> dict:
        """Compile all Python files in path.

        Args:
            path: Path to compile

        Returns:
            Compilation result dict
        """
        compile_path = Path(path)
        files_compiled = 0
        files_failed = 0
        errors = []

        self.logger.info(f"Starting compilation of path: {path}")

        for py_file in compile_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue

            try:
                py_compile.compile(str(py_file), doraise=True)
                files_compiled += 1
                self.logger.debug(f"Compiled: {py_file}")
            except py_compile.PyCompileError as e:
                files_failed += 1
                error_info = {
                    'file': str(py_file),
                    'error': str(e)
                }
                errors.append(error_info)
                self.logger.warning(f"Failed to compile {py_file}: {e}")

        result = {
            'success': len(errors) == 0,
            'files_compiled': files_compiled,
            'files_failed': files_failed,
            'errors': errors
        }

        self.logger.info(
            f"Compilation complete: {files_compiled} success, {files_failed} failed"
        )
        self.metrics.increment('compile.all.calls', value=1)

        return result

    def compile_interface(self, interface_name: str, base_path: str = '.') -> dict:
        """Compile single interface.

        Args:
            interface_name: Interface directory name (e.g., 'cache', 'logging')
            base_path: Base path containing interfaces

        Returns:
            Compilation result dict
        """
        interface_path = Path(base_path) / interface_name

        if not interface_path.exists():
            self.logger.error(f"Interface not found: {interface_path}")
            return {
                'success': False,
                'files_compiled': 0,
                'files_failed': 0,
                'errors': [{'file': str(interface_path), 'error': 'Interface not found'}]
            }

        files_compiled = 0
        files_failed = 0
        errors = []

        self.logger.info(f"Compiling interface: {interface_name} at {interface_path}")

        for py_file in interface_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue

            try:
                py_compile.compile(str(py_file), doraise=True)
                files_compiled += 1
                self.logger.debug(f"Compiled: {py_file}")
            except py_compile.PyCompileError as e:
                files_failed += 1
                error_info = {
                    'file': str(py_file),
                    'error': str(e)
                }
                errors.append(error_info)
                self.logger.warning(f"Failed to compile {py_file}: {e}")

        result = {
            'success': len(errors) == 0,
            'interface': interface_name,
            'files_compiled': files_compiled,
            'files_failed': files_failed,
            'errors': errors
        }

        self.logger.info(
            f"Interface {interface_name} compilation complete: "
            f"{files_compiled} success, {files_failed} failed"
        )
        self.metrics.increment('compile.interface.calls', value=1)

        return result

    def compile_file(self, file_path: str) -> dict:
        """Compile single Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Compilation result dict
        """
        py_file = Path(file_path)

        if not py_file.exists():
            self.logger.error(f"File not found: {py_file}")
            return {
                'success': False,
                'file': str(py_file),
                'error': 'File not found'
            }

        if py_file.suffix != '.py':
            self.logger.error(f"Not a Python file: {py_file}")
            return {
                'success': False,
                'file': str(py_file),
                'error': 'Not a Python file'
            }

        self.logger.info(f"Compiling file: {file_path}")

        try:
            py_compile.compile(str(py_file), doraise=True)
            self.logger.info(f"Successfully compiled: {file_path}")
            self.metrics.increment('compile.file.success', value=1)
            return {
                'success': True,
                'file': str(py_file),
                'compiled': True
            }
        except py_compile.PyCompileError as e:
            self.logger.warning(f"Failed to compile {file_path}: {e}")
            self.metrics.increment('compile.file.failure', value=1)
            return {
                'success': False,
                'file': str(py_file),
                'error': str(e)
            }


__all__ = ['CompileFactory']
