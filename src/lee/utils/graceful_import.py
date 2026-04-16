# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Create graceful import decorator with stubs


"""graceful_import.py - Graceful Import Decorator

Version: 2026-04-11_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from functools import wraps
from typing import Callable, Any


def graceful_import(module_path, stub_return: Any = None):
    """Decorator to handle imports with automatic stub generation.

    Args:
        module_path: Python module path (str or list of str)
        stub_return: Value for stubs to return (default: error dict)

    Returns:
        Decorator that handles ImportError and creates stubs
    """
    def decorator(import_func: Callable) -> Callable:
        @wraps(import_func)
        def wrapper(*args, **kwargs):
            try:
                result = import_func(*args, **kwargs)
                # Handle both string and list of strings
                if isinstance(module_path, str):
                    module_name = module_path.split('.')[-1].upper()
                    wrapper.__dict__[f'_{module_name}_AVAILABLE'] = True
                elif isinstance(module_path, list):
                    for path in module_path:
                        mod_name = path.split('.')[-1].upper()
                        wrapper.__dict__[f'_{mod_name}_AVAILABLE'] = True
                return result
            except ImportError as e:
                # Handle both string and list of strings
                if isinstance(module_path, str):
                    module_name = module_path.split('.')[-1].upper()
                    wrapper.__dict__[f'_{module_name}_AVAILABLE'] = False
                    wrapper.__dict__[f'_{module_name}_IMPORT_ERROR'] = str(e)
                elif isinstance(module_path, list):
                    for path in module_path:
                        mod_name = path.split('.')[-1].upper()
                        wrapper.__dict__[f'_{mod_name}_AVAILABLE'] = False
                        wrapper.__dict__[f'_{mod_name}_IMPORT_ERROR'] = str(e)
                # Return stub functions
                if stub_return is not None:
                    return stub_return
                return {
                    'success': False,
                    'error': 'Module not available'
                }
        return wrapper
    return decorator


def create_stubs(function_names: list[str], module_name: str, error_msg: str = None):
    """Create stub functions for unavailable module.

    Args:
        function_names: List of function names to create stubs for
        module_name: Module name for error messages
        error_msg: Custom error message (optional)

    Returns:
        Dict of function_name -> stub_function
    """
    stubs = {}
    for func_name in function_names:
        def stub(**_kwargs):
            if error_msg:
                return {"success": False, "error": error_msg}
            return {"success": False, "error": f'{module_name} not available'}
        stub.__name__ = func_name
        stubs[func_name] = stub
    return stubs


__all__ = [
    'graceful_import',
    'create_stubs',
]
