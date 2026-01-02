"""
EE Scanner Domain - UG-ISP Compliant Universal Gateway for Scanner Operations.

Domain Gateway for scanner operations including:
- UG-ISP compliance scanning
- Python file compilation
- Test execution
- Cache management
- Architecture validation
- Report generation

EE 2.1 Architecture (100% EE-UG Compliant):
    - ScannerGateway - EE 2.1 compliant domain gateway
    - ScannerGatewayFactory - Factory for creating gateway instances
    - NO backward compatibility with EE 2.0
    - NO legacy execute_operation() function
    - Factory-driven construction only
    - DI-mandatory pattern

Usage (EE 2.1):
    # Create gateway factory with DI
    from EE.scanner import ScannerGatewayFactory

    factory = ScannerGatewayFactory(
        get_logger=logger_factory,
        get_metrics=metrics_factory,
        get_config=config_factory,
        call_operation=cross_domain_caller
    )

    # Create gateway instance
    gateway = factory.create_gateway()

    # Execute operations
    result = gateway.execute_domain_operation(
        interface="scan",
        operation="scan",
        path="D:/Code/EE/src"
    )

Architecture:
    External Code
        ↓ (execute_domain_operation with interface name)
    Scanner Gateway (ScannerGateway - DomainGateway subclass)
        ↓ (factory.create_interface())
    Scanner Interface (Interface router)
        ↓ (operation dispatch)
    Scanner Factory (Factory with business logic)
        ↓ (implementation)
    Result

UG-ISP Pattern:
    External Code
        ↓ (execute_operation with ScannerInterface)
    Scanner Gateway (ISP Router)
        ↓ (O(1) dispatch dictionary)
    Scanner Interface Modules (SCAN, COMPILE, TEST, etc.)
        ↓ (implementation)
    Scanner Implementation

Based on:
    - EE/src/scanner/ (migrated to EE/scanner/)
    - EE/universal_gateway/domain_gateway.py (DomainGateway base class)
"""

from __future__ import annotations

# EE 2.1 Gateway Components
from EE.scanner.gateway import ScannerGateway, ScannerGatewayFactory

# Import enums
from EE.scanner.gateway.gateway_enums import ScannerInterface

# Import core components
from EE.scanner.core import (
    # False Positive Handler
    Violation,
    ConfidenceLevel,
    FalsePositivePatterns,
    FalsePositiveAnalyzer,
    ConfirmedFalsePositiveManager,
    ViolationReporter,
    create_default_false_positives_config,

    # Invalid Operation Detector
    InvalidOperationViolation,
    InvalidOperationScanResult,
    InvalidOperationDetector,

    # Custom Implementation Patterns
    Severity,
    PatternMatch,
    CustomImplementationPatternMatcher,
    EE_CUSTOM_IMPL_PATTERNS,
    scan_custom_impl_directory,

    # Parameter Validator
    ParameterConfidenceLevel,
    SeverityLevel,
    ParameterViolation,
    ParameterScanResult,
    ParameterValidator,
)

__all__ = [
    # EE 2.1 Gateway (Factory-driven, DI-mandatory)
    'ScannerGateway',
    'ScannerGatewayFactory',

    # Enums
    'ScannerInterface',

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

__version__ = '2.1.0'
