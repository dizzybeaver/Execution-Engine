"""Scanner Test Interface - EE 2.1 Compliant.

EE 2.1 Architecture:
- Interface is created via factory function
- Use ScannerGateway for operations
- NO direct execute_test_operation() exports (removed in EE 2.1)

Note: This interface file (scanner_test_interface.py) still contains EE 2.0
legacy code with 'from gateway import execute'. It needs migration to EE 2.1
factory pattern with DI. For now, the interface is disabled to prevent
legacy usage.
"""

from __future__ import annotations

__all__ = []  # Intentionally empty - use ScannerGateway

