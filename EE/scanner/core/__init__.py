"""
EE Scanner Core Components
Version: 1.0.0
Date: 2025-12-29

Core detection components for EE UG-ISP Architecture Scanner.

Components:
- false_positive_handler: Transparent false positive detection and reporting
- invalid_operation_detector: Validates execute_operation() interface/operation combinations
- custom_impl_patterns: Detects custom implementations bypassing Gateway
- parameter_validator: Validates parameter names in execute_operation() calls

UG-ISP COMPLIANCE:
- NO os.environ/os.getenv() calls
- ALL config access via gateway
- Lazy imports only
- Inline correlation IDs
"""

from EE.scanner.core.false_positive_handler import (
    Violation,
    ConfidenceLevel,
    FalsePositivePatterns,
    FalsePositiveAnalyzer,
    ConfirmedFalsePositiveManager,
    ViolationReporter,
    create_default_false_positives_config,
)

from EE.scanner.core.invalid_operation_detector import (
    Violation as InvalidOperationViolation,
    ScanResult as InvalidOperationScanResult,
    InvalidOperationDetector,
)

from EE.scanner.core.custom_impl_patterns import (
    Severity,
    PatternMatch,
    CustomImplementationPatternMatcher,
    EE_CUSTOM_IMPL_PATTERNS,
    scan_directory as scan_custom_impl_directory,
)

from EE.scanner.core.parameter_validator import (
    ConfidenceLevel as ParameterConfidenceLevel,
    SeverityLevel,
    ParameterViolation,
    ParameterScanResult,
    ParameterValidator,
)

__all__ = [
    # False Positive Handler
    'Violation',
    'ConfidenceLevel',
    'FalsePositivePatterns',
    'FalsePositiveAnalyzer',
    'ConfirmedFalsePositiveManager',
    'ViolationReporter',
    'create_default_false_positives_config',

    # Invalid Operation Detector
    'InvalidOperationViolation',
    'InvalidOperationScanResult',
    'InvalidOperationDetector',

    # Custom Implementation Patterns
    'Severity',
    'PatternMatch',
    'CustomImplementationPatternMatcher',
    'EE_CUSTOM_IMPL_PATTERNS',
    'scan_custom_impl_directory',

    # Parameter Validator
    'ParameterConfidenceLevel',
    'SeverityLevel',
    'ParameterViolation',
    'ParameterScanResult',
    'ParameterValidator',
]

__version__ = '1.0.0'
