"""Cleanup interface router (UG-ISP Router).

Cache cleanup operations.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

from pathlib import Path
from typing import Any


def _cleanup_all(path: str = '.') -> dict:
    """Clean all cache files and directories.

    Args:
        path: Path to clean

    Returns:
        Cleanup result dict
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
        except Exception as e:
            errors.append({
                'path': str(pycache),
                'error': str(e)
            })

    # Remove .pyc files (in case any remain outside __pycache__)
    for pyc_file in clean_path.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            pyc_files += 1
        except Exception as e:
            errors.append({
                'path': str(pyc_file),
                'error': str(e)
            })

    # Remove .pyo files
    for pyo_file in clean_path.rglob('*.pyo'):
        try:
            pyo_file.unlink()
            pyo_files += 1
        except Exception as e:
            errors.append({
                'path': str(pyo_file),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'pycache_dirs_removed': pycache_dirs,
        'pyc_files_removed': pyc_files,
        'pyo_files_removed': pyo_files,
        'total_items_removed': pycache_dirs + pyc_files + pyo_files,
        'errors': errors
    }


def _cleanup_pycache(path: str = '.') -> dict:
    """Clean only __pycache__ directories.

    Args:
        path: Path to clean

    Returns:
        Cleanup result dict
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
        except Exception as e:
            errors.append({
                'path': str(pycache),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'dirs_removed': dirs_removed,
        'files_removed': files_removed,
        'errors': errors
    }


def _cleanup_compiled(path: str = '.') -> dict:
    """Clean only compiled files (.pyc, .pyo).

    Args:
        path: Path to clean

    Returns:
        Cleanup result dict
    """
    clean_path = Path(path)
    pyc_count = 0
    pyo_count = 0
    errors = []

    for pyc_file in clean_path.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            pyc_count += 1
        except Exception as e:
            errors.append({
                'path': str(pyc_file),
                'error': str(e)
            })

    for pyo_file in clean_path.rglob('*.pyo'):
        try:
            pyo_file.unlink()
            pyo_count += 1
        except Exception as e:
            errors.append({
                'path': str(pyo_file),
                'error': str(e)
            })

    return {
        'success': len(errors) == 0,
        'pyc_files_removed': pyc_count,
        'pyo_files_removed': pyo_count,
        'total_files_removed': pyc_count + pyo_count,
        'errors': errors
    }


# Dispatch dictionary - O(1) operation routing
_CLEANUP_DISPATCH = {
    'all': lambda **kw: _cleanup_all(kw.get('path', '.')),
    'pycache': lambda **kw: _cleanup_pycache(kw.get('path', '.')),
    'compiled': lambda **kw: _cleanup_compiled(kw.get('path', '.')),
}


def execute_cleanup_operation(operation: str, **kwargs) -> Any:
    """Route cleanup operation requests.

    Args:
        operation: Operation name (all, pycache, compiled)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown
    """
    if operation not in _CLEANUP_DISPATCH:
        raise ValueError(
            f"Unknown cleanup operation: '{operation}'. "
            f"Valid: {', '.join(_CLEANUP_DISPATCH.keys())}"
        )

    handler = _CLEANUP_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_cleanup_operation']
