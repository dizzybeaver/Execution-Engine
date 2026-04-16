#!/usr/bin/env python3
"""Error signature data model for diagnosis system."""

from dataclasses import dataclass


@dataclass
class ErrorSignature:
    """Unique signature for error pattern matching.

    Attributes:
        error_type: Exception type name (e.g., "ConnectionError")
        error_category: Category of error (e.g., "database", "network", "validation")
        source_module: Module where error occurred
    """

    error_type: str
    error_category: str
    source_module: str

    def __hash__(self):
        """Generate hash for use as dictionary key."""
        return hash((self.error_type, self.error_category, self.source_module))

    def __eq__(self, other):
        """Check equality with another ErrorSignature."""
        if not isinstance(other, ErrorSignature):
            return False
        return (self.error_type == other.error_type
                and self.error_category == other.error_category
                and self.source_module == other.source_module)
