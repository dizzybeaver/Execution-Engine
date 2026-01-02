"""Validate Factory - EE 2.1 Compliant

Factory contains all business logic for validation operations.

Based on: EE/scanner/archive/scanner_validate_interface.py.legacy
"""

from __future__ import annotations
from typing import Any, Callable, Dict


class ValidateFactory:
    """Factory for validation operations (EE 2.1 compliant).

    Responsibilities:
    - Implement all validation business logic
    - Use DI (logger, metrics, config, call_operation)
    - NO interface logic (that's in the interface router)
    - Delegate scan operations via call_operation

    EE 2.1 Pattern:
    - All business logic lives here
    - Interface router is thin (no logic)
    - DI for all dependencies
    - No global state
    """

    def __init__(
        self,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str, Any], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize validate factory with DI.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
        """
        self.logger = get_logger("scanner.validate.factory")
        self.metrics = get_metrics("scanner.validate.factory")
        self._call_operation = call_operation

    def validate_architecture(self, path: str = '.') -> Dict:
        """Validate UG-ISP architecture compliance.

        Args:
            path: Path to validate

        Returns:
            Validation result dict with:
                - success: True if validation completed
                - compliant: True if architecture is compliant
                - violation_count: Total violations found
                - critical_violations: Number of CRITICAL violations
                - high_violations: Number of HIGH violations
                - compliance_score: Score 0-100
                - scan_result: Full scan results
        """
        self.logger.debug(f"Validating architecture at {path}")

        # Delegate to SCAN interface via call_operation
        result = self._call_operation(
            'scan',  # ScannerInterface.SCAN
            'scan',
            path=path,
            report_dir='reports/validation'
        )

        # Determine compliance
        violations = result.get('violations_found', 0)
        critical = sum(1 for v in result.get('violations', [])
                       if v.get('severity') == 'CRITICAL')
        high = sum(1 for v in result.get('violations', [])
                   if v.get('severity') == 'HIGH')

        # Architecture compliance requires:
        # - No CRITICAL violations (gateway bypass, cross-interface imports)
        # - No HIGH violations (forbidden imports, debug helpers)
        is_compliant = (critical == 0 and high == 0)

        compliance_result = {
            'success': True,
            'compliant': is_compliant,
            'violation_count': violations,
            'critical_violations': critical,
            'high_violations': high,
            'compliance_score': max(0, 100 - (critical * 20) - (high * 10)),
            'scan_result': result
        }

        self.logger.info(
            f"Architecture validation: compliant={is_compliant}, "
            f"critical={critical}, high={high}, score={compliance_result['compliance_score']}"
        )

        return compliance_result

    def validate_imports(self, path: str = '.') -> Dict:
        """Validate import patterns only.

        Args:
            path: Path to validate

        Returns:
            Validation result dict with:
                - success: True if validation completed
                - import_compliant: True if no CRITICAL import violations
                - import_violations: Number of import violations
                - critical_imports: Number of CRITICAL import violations
                - violations: List of import violations
        """
        self.logger.debug(f"Validating imports at {path}")

        # Delegate to SCAN interface
        result = self._call_operation(
            'scan',
            'scan',
            path=path,
            report_dir='reports/validation/imports'
        )

        # Filter for import violations only
        import_violations = [
            v for v in result.get('violations', [])
            if v.get('violation_type') in [
                'FORBIDDEN_IMPORT',
                'CROSS_INTERFACE_IMPORT'
            ]
        ]

        critical_imports = sum(1 for v in import_violations
                               if v.get('severity') == 'CRITICAL')

        import_result = {
            'success': True,
            'import_compliant': critical_imports == 0,
            'import_violations': len(import_violations),
            'critical_imports': critical_imports,
            'violations': import_violations
        }

        self.logger.info(
            f"Import validation: compliant={import_result['import_compliant']}, "
            f"violations={len(import_violations)}, critical={critical_imports}"
        )

        return import_result

    def validate_patterns(self, path: str = '.') -> Dict:
        """Validate against known UG-ISP patterns.

        Args:
            path: Path to validate

        Returns:
            Validation result dict with:
                - success: True if validation completed
                - patterns_compliant: True if all patterns are compliant
                - pattern_compliance: Dict of pattern -> compliant bool
                - pattern_violations: Dict of pattern -> violation count
                - violations_by_pattern: Detailed violations by pattern
        """
        self.logger.debug(f"Validating patterns at {path}")

        # Delegate to SCAN interface
        result = self._call_operation(
            'scan',
            'scan',
            path=path,
            report_dir='reports/validation/patterns'
        )

        # Categorize violations by pattern
        violations = result.get('violations', [])

        pattern_violations = {
            'internal_debug_helpers': [
                v for v in violations
                if v.get('violation_type') == 'INTERNAL_DEBUG_HELPER'
            ],
            'gateway_bypass': [
                v for v in violations
                if v.get('violation_type') == 'FORBIDDEN_IMPORT'
                and 'gateway' in v.get('description', '').lower()
            ],
            'cross_interface': [
                v for v in violations
                if v.get('violation_type') == 'CROSS_INTERFACE_IMPORT'
            ],
            'interface_imports': [
                v for v in violations
                if v.get('description', '').startswith('Direct interface import')
            ]
        }

        # Pattern compliance check
        pattern_compliance = {
            pattern: len(violations_list) == 0
            for pattern, violations_list in pattern_violations.items()
        }

        patterns_result = {
            'success': True,
            'patterns_compliant': all(pattern_compliance.values()),
            'pattern_compliance': pattern_compliance,
            'pattern_violations': {
                pattern: len(violations_list)
                for pattern, violations_list in pattern_violations.items()
            },
            'violations_by_pattern': pattern_violations
        }

        self.logger.info(
            f"Pattern validation: compliant={patterns_result['patterns_compliant']}, "
            f"patterns={list(pattern_compliance.keys())}"
        )

        return patterns_result


__all__ = ['ValidateFactory']
