"""interface_ast_scanner package
Version: 2026-04-06
Purpose: AST_SCANNER interface router - AST analysis and code quality scanning
License: Apache 2.0

SECURITY (2026-03-22_2):
- Added path traversal validation to prevent directory escape attacks
- Validates path parameter against allowlist and checks for traversal sequences

This interface provides gateway routing for AST scanning operations, including:
- Code quality analysis (complexity, length, naming)
- Clone detection (Type 1-4 duplicate detection)
- Import analysis (circular dependencies, unused imports)
- Gateway compliance checking (LEE-specific)
- Interface harvesting (extract interface definitions)
- Control flow analysis (CFG/DFG generation)
- Completeness verification (implementation tracking)
- Deep analysis (combined control + data flow)

The original 1742-line file has been split into focused modules:
- ast_scanner_helpers.py: Helper functions, security validation, and constants
- interface_ast_scanner.py: Main implementation with router and inline scans

All functions are re-exported here for backward compatibility.
"""

# Import helper functions and constants
from lee.interface.interface_ast_scanner.ast_scanner_helpers import (
    _validate_scan_path,
    DEFAULT_COMPLEXITY_THRESHOLD,
    DEFAULT_MAX_COMPLEXITY,
    DEFAULT_DUPLICATION_THRESHOLD,
    DEFAULT_CLONE_TYPE,
    DEFAULT_FUNCTION_LENGTH_THRESHOLD,
    DEFAULT_CACHE_SIZE_LIMIT,
    DEFAULT_EXCLUDE_PATTERNS,
)

# Import remaining functions from main file
from lee.interface.interface_ast_scanner.interface_ast_scanner import (
    _scan_inline,
    _scan_quality_inline,
    _scan_duplicate_inline,
    _scan_all_inline,
    _json_format_handler,
    _markdown_format_handler,
    _txt_format_handler,
    _console_format_handler,
    validate_format_type,
    get_format_metadata,
    _format_result_inline,
    _get_available_scans_inline,
    _get_clone_types_inline,
    _scan_import_pattern_inline,
    _scan_gateway_pattern_inline,
    _scan_exception_pattern_inline,
    _scan_self_referential_gateway_inline,
    _scan_parameter_collision_inline,
    _scan_wrong_operation_name_inline,
    _scan_misindented_import_inline,
    _scan_empty_except_block_inline,
    _scan_malformed_docstring_inline,
    _scan_direct_wrapper_import_inline,
    _scan_security_bypass_inline,
    _scan_relative_import_inline,
    execute_ast_scanner_operation,
    list_ast_scanner_operations,
)

__all__ = [
    # Helpers and constants
    "_validate_scan_path",
    "DEFAULT_COMPLEXITY_THRESHOLD",
    "DEFAULT_MAX_COMPLEXITY",
    "DEFAULT_DUPLICATION_THRESHOLD",
    "DEFAULT_CLONE_TYPE",
    "DEFAULT_FUNCTION_LENGTH_THRESHOLD",
    "DEFAULT_CACHE_SIZE_LIMIT",
    "DEFAULT_EXCLUDE_PATTERNS",
    # Scanner functions
    "_scan_inline",
    "_scan_quality_inline",
    "_scan_duplicate_inline",
    "_scan_all_inline",
    "_json_format_handler",
    "_markdown_format_handler",
    "_txt_format_handler",
    "_console_format_handler",
    "validate_format_type",
    "get_format_metadata",
    "_format_result_inline",
    "_get_available_scans_inline",
    "_get_clone_types_inline",
    "_scan_import_pattern_inline",
    "_scan_gateway_pattern_inline",
    "_scan_exception_pattern_inline",
    "_scan_self_referential_gateway_inline",
    "_scan_parameter_collision_inline",
    "_scan_wrong_operation_name_inline",
    "_scan_misindented_import_inline",
    "_scan_empty_except_block_inline",
    "_scan_malformed_docstring_inline",
    "_scan_direct_wrapper_import_inline",
    "_scan_security_bypass_inline",
    "_scan_relative_import_inline",
    "execute_ast_scanner_operation",
    "list_ast_scanner_operations",
]
