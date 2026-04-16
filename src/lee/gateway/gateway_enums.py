"""gateway_enums.py - Gateway Interface Enumeration
Version: 2025-12-13_2
Date: 2026-03-05
Description: Shared enum to prevent circular imports

CHANGES (2025-12-13_1):
- ADDED: DIAGNOSIS interface
- ADDED: TEST interface

CHANGES (2025-12-13_2):
- ADDED: LAZY_IMPORT interface for LIGS (Lazy Import Gateway System)

CHANGES (2026-03-05):
- ADDED: AST_SCANNER interface for AST analysis and code quality scanning

CHANGES (2026-03-09):
- ADDED: DATABASE interface for database operations
- ADDED: BATCH interface for batch operations
- ADDED: VALIDATION interface for input validation
- ADDED: MONITORING interface for health checks and alerting

CHANGES (2026-03-25):
- CONSOLIDATED: DATABASE and BATCH interfaces into DATA interface
- Removed: DATABASE, BATCH interfaces
- Added: DATA interface (consolidates database + batch operations)

CREATED: Extracted GatewayInterface from gateway_core.py
PURPOSE: Break circular import between gateway_core and gateway_wrappers

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from enum import Enum


class GatewayInterface(Enum):
    """Gateway interface enumeration for SUGA-ISP pattern routing.

    This enum defines all available gateway interfaces in the LEE system.
    Each interface represents a service network that can be accessed through
    the gateway's execute_operation() function.

    Architecture Pattern (SUGA-ISP):
        - Gateway = ISP (Internet Service Provider) - Central routing hub
        - Interface = Router - Routes to specific service networks

    Usage:
        from lee.gateway import execute_operation, GatewayInterface

        # Execute operation through gateway
        result = execute_operation(
            GatewayInterface.LOGGING,
            'log_info',
            message='Hello world',
            corr_id='abc123'
        )

    Available Interfaces:
        CACHE: Cache operations for storing and retrieving data
        LOGGING: Structured logging with correlation IDs
        SECURITY: Security validation and sanitization
        METRICS: Performance and operational metrics recording
        CONFIG: Configuration management and retrieval
        SINGLETON: Singleton pattern instance management
        INITIALIZATION: System initialization and startup tasks
        HTTP_CLIENT: HTTP operations with retry logic
        WEBSOCKET: WebSocket connection management
        CIRCUIT_BREAKER: Circuit breaker pattern for fault tolerance
        UTILITY: General utility functions
        DEBUG: Debugging and diagnostic operations
        DIAGNOSIS: Health checks and system diagnostics
        TEST: Testing interface for development and validation
        CLOUDWATCH: CloudWatch metrics integration
        PERFORMANCE: Performance observability and profiling
        LAZY_IMPORT: Lazy module loading system (LIGS)
        AST_SCANNER: AST analysis and code quality scanning
        METADATA: Metadata, event tracking, and system information (2026-03-08)
        VALIDATION: Centralized input validation (2026-03-09)
        DATA: Data operations (database + batch processing, 2026-03-25)

    Thread Safety:
        All gateway interfaces are thread-safe and can be called from
        multiple threads concurrently.

    Error Handling:
        Operations should gracefully handle errors and return appropriate
        error values rather than raising exceptions, unless the error
        is critical and should propagate.
    """

    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    SINGLETON = "singleton"
    INITIALIZATION = "initialization"
    HTTP_CLIENT = "http_client"
    WEBSOCKET = "websocket"
    CIRCUIT_BREAKER = "circuit_breaker"
    UTILITY = "utility"
    DEBUG = "debug"
    DIAGNOSIS = "diagnosis"
    TEST = "test"
    CLOUDWATCH = "cloudwatch"
    PERFORMANCE = "performance"
    LAZY_IMPORT = "lazy_import"
    AST_SCANNER = "ast_scanner"
    METADATA = "metadata"
    # Phase 5.1: New interfaces (2026-03-09)
    VALIDATION = "validation"
    # Phase 6: OBSERVABILITY consolidation (2026-03-24)
    # Consolidates: MONITORING, DIAGNOSIS, PERFORMANCE
    OBSERVABILITY = "observability"
    # Phase 7: DATA consolidation (2026-03-25)
    # Consolidates: DATABASE, BATCH
    DATA = "data"


__all__ = ["GatewayInterface"]
