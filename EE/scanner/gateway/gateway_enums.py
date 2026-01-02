"""Scanner interface enumeration for EE Universal Gateway routing.

UG-ISP Compliant:
    - All operations defined as enum values
    - Clear categorization of scanner operations
    - Direct mapping to gateway routes

Architecture:
    - ScannerInterface.SCAN → scanner.scan.*
    - ScannerInterface.COMPILE → scanner.compile.*
    - ScannerInterface.TEST → scanner.test.*
    - ScannerInterface.CLEANUP → scanner.cleanup.*
    - ScannerInterface.VALIDATE → scanner.validate.*
    - ScannerInterface.REPORT → scanner.report.*
    - ScannerInterface.CACHE → scanner.cache.*
    - ScannerInterface.UTILITY → scanner.utility.*

Usage:
    from scanner.gateway import execute_operation, ScannerInterface

    # Run scan
    result = execute_operation(
        ScannerInterface.SCAN,
        'scan',
        path='D:\\Code\\EE\\src'
    )

    # Compile Python files
    result = execute_operation(
        ScannerInterface.COMPILE,
        'compile',
        path='D:\\Code\\EE\\src',
        recursive=True
    )

    # Generate report
    report = execute_operation(
        ScannerInterface.REPORT,
        'generate',
        scan_id='2025-12-29_001'
    )
"""

from __future__ import annotations

from enum import Enum


class ScannerInterface(str, Enum):
    """EE Gateway Scanner interface enumeration for unified scanner.

    All scanner operations MUST go through execute_operation() with these interfaces.
    This is the ONLY supported pattern for scanner operations in EE.

    UG-ISP Compliance:
        - All operations use this enum for interface selection
        - No direct interface instantiation
        - Clear operation categorization
        - Type-safe interface routing

    Available Interfaces:
        SCAN: UG-ISP compliance scanning operations
        COMPILE: Python file compilation operations
        TEST: Test execution operations
        CLEANUP: Cache cleanup operations
        VALIDATE: Architecture validation operations
        REPORT: Report generation operations
        CACHE: Caching operations for scan results
        UTILITY: Utility functions (file operations, datetime, formatting)

    Example:
        from scanner.gateway import execute_operation, ScannerInterface

        # Run UG-ISP compliance scan
        result = execute_operation(
            ScannerInterface.SCAN,
            'scan',
            path='D:\\Code\\EE\\src'
        )

        # Generate report
        report = execute_operation(
            ScannerInterface.REPORT,
            'generate',
            scan_id='2025-12-29_001'
        )

        # Validate architecture
        validation = execute_operation(
            ScannerInterface.VALIDATE,
            'validate_architecture',
            path='D:\\Code\\EE\\src'
        )
    """
    SCAN = "scan"
    COMPILE = "compile"
    TEST = "test"
    CLEANUP = "cleanup"
    VALIDATE = "validate"
    REPORT = "report"
    CACHE = "cache"
    UTILITY = "utility"

    def __str__(self) -> str:
        """Return enum value as string."""
        return self.value

    @classmethod
    def get_all_interfaces(cls) -> list[str]:
        """Get list of all interface values.

        Returns:
            List of all scanner interface names
        """
        return [interface.value for interface in cls]

    @classmethod
    def is_valid_interface(cls, interface_name: str) -> bool:
        """Check if interface name is valid.

        Args:
            interface_name: Interface name to validate

        Returns:
            True if interface exists, False otherwise
        """
        return interface_name in cls.get_all_interfaces()


__all__ = [
    'ScannerInterface',
]
