"""
FileIO Interface - Operations Domain

File I/O operations.
"""

from EE.operations.fileio.fileio_interface import execute_fileio_operation
from EE.operations.fileio.fileio_factory import FileIOFactory

__all__ = [
    'execute_fileio_operation',
    'FileIOFactory',
]
