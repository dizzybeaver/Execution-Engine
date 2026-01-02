"""Compile interface router (UG-ISP Router).

Python file compilation operations.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

import py_compile
from pathlib import Path
from typing import Any, List


def _compile_all(path: str = '.') -> dict:
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

    for py_file in compile_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        try:
            py_compile.compile(str(py_file), doraise=True)
            files_compiled += 1
        except py_compile.PyCompileError as e:
            files_failed += 1
            errors.append({
                'file': str(py_file),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'files_compiled': files_compiled,
        'files_failed': files_failed,
        'errors': errors
    }


def _compile_interface(interface_name: str, base_path: str = '.') -> dict:
    """Compile single interface.

    Args:
        interface_name: Interface directory name (e.g., 'cache', 'logging')
        base_path: Base path containing interfaces

    Returns:
        Compilation result dict
    """
    interface_path = Path(base_path) / interface_name

    if not interface_path.exists():
        return {
            'success': False,
            'files_compiled': 0,
            'files_failed': 0,
            'errors': [{'file': str(interface_path), 'error': 'Interface not found'}]
        }

    files_compiled = 0
    files_failed = 0
    errors = []

    for py_file in interface_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        try:
            py_compile.compile(str(py_file), doraise=True)
            files_compiled += 1
        except py_compile.PyCompileError as e:
            files_failed += 1
            errors.append({
                'file': str(py_file),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'interface': interface_name,
        'files_compiled': files_compiled,
        'files_failed': files_failed,
        'errors': errors
    }


def _compile_file(file_path: str) -> dict:
    """Compile single Python file.

    Args:
        file_path: Path to Python file

    Returns:
        Compilation result dict
    """
    py_file = Path(file_path)

    if not py_file.exists():
        return {
            'success': False,
            'file': str(py_file),
            'error': 'File not found'
        }

    if py_file.suffix != '.py':
        return {
            'success': False,
            'file': str(py_file),
            'error': 'Not a Python file'
        }

    try:
        py_compile.compile(str(py_file), doraise=True)
        return {
            'success': True,
            'file': str(py_file),
            'compiled': True
        }
    except py_compile.PyCompileError as e:
        return {
            'success': False,
            'file': str(py_file),
            'error': str(e)
        }


# Dispatch dictionary - O(1) operation routing
_COMPILE_DISPATCH = {
    'all': lambda **kw: _compile_all(kw.get('path', '.')),
    'interface': lambda **kw: _compile_interface(
        kw.get('interface_name'),
        kw.get('base_path', '.')
    ),
    'file': lambda **kw: _compile_file(kw.get('file_path')),
}


def execute_compile_operation(operation: str, **kwargs) -> Any:
    """Route compile operation requests.

    Args:
        operation: Operation name (all, interface, file)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown
    """
    if operation not in _COMPILE_DISPATCH:
        raise ValueError(
            f"Unknown compile operation: '{operation}'. "
            f"Valid: {', '.join(_COMPILE_DISPATCH.keys())}"
        )

    handler = _COMPILE_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_compile_operation']
