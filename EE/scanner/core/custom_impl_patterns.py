"""
Custom Implementation Pattern Library for EE UG-ISP Scanner

Version: 1.0.0
Date: 2025-12-29
Purpose: Detect custom implementations that bypass Gateway ISP routing

This library provides pattern matching for common custom implementations
that violate UG-ISP architecture by bypassing the Gateway (ISP).

UG-ISP COMPLIANCE:
- NO os.environ/os.getenv() calls
- ALL config access via gateway
- Lazy imports only
- Inline correlation IDs
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class Severity(Enum):
    """Violation severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PatternMatch:
    """Represents a single pattern match found in code."""
    file_path: str
    line_number: int
    pattern_name: str
    severity: Severity
    found_code: str
    gateway_interface: str
    gateway_operation: str
    fix_pattern: str
    description: str
    context_lines: List[str] = field(default_factory=list)


class CustomImplementationPatternMatcher:
    """
    Pattern matcher for detecting custom implementations that bypass Gateway.

    Uses regex patterns to identify code that should use Gateway interfaces
    but instead implements functionality directly.
    """

    def __init__(self):
        """Initialize pattern matcher with comprehensive pattern database."""
        self.patterns = self._build_pattern_database()
        self.compiled_patterns = self._compile_patterns()

    def _build_pattern_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Build comprehensive pattern database for all custom implementations.

        Returns:
            Dict mapping pattern categories to their detection patterns
        """
        return {
            # CRITICAL: Internal Debug Helpers (Architecture Violation)
            'internal_debug_helper': {
                'name': 'Internal Debug Helper Function',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'def _debug_log\(',
                    r'def _debug_timing\(',
                    r'def _generate_correlation_id\(',
                    r'def _log_debug\(',
                    r'def _log_info\(',
                    r'def _log_error\(',
                ],
                'gateway_interface': 'DEBUG',
                'gateway_operation': 'N/A',
                'fix': 'Remove helper function. Use execute_operation(GatewayInterface.DEBUG, ...) directly in all functions.',
                'description': 'Internal debug helper bypasses Gateway ISP routing. All debug operations must go through Gateway.',
                'why_critical': 'Violates UG-ISP architecture by creating parallel routing path that bypasses ISP (Gateway).'
            },

            # HIGH: Direct logging calls
            'direct_logging_info': {
                'name': 'Direct logging.info() Call',
                'severity': Severity.HIGH,
                'patterns': [
                    r'logging\.info\(',
                    r'logger\.info\(',
                    r'import logging\s*\n.*?logging\.info\(',
                ],
                'gateway_interface': 'LOGGING',
                'gateway_operation': 'info',
                'fix': 'execute_operation(GatewayInterface.LOGGING, \'info\', message=message, **context)',
                'description': 'Direct logging.info() call instead of Gateway LOGGING interface',
                'why_critical': 'Bypasses structured logging and Gateway routing, breaks audit trail.'
            },

            'direct_logging_error': {
                'name': 'Direct logging.error() Call',
                'severity': Severity.HIGH,
                'patterns': [
                    r'logging\.error\(',
                    r'logger\.error\(',
                    r'import logging\s*\n.*?logging\.error\(',
                ],
                'gateway_interface': 'LOGGING',
                'gateway_operation': 'error',
                'fix': 'execute_operation(GatewayInterface.LOGGING, \'error\', message=message, error=error, **context)',
                'description': 'Direct logging.error() call instead of Gateway LOGGING interface',
                'why_critical': 'Bypasses structured logging and Gateway routing, breaks error tracking.'
            },

            'direct_logging_warning': {
                'name': 'Direct logging.warning() Call',
                'severity': Severity.HIGH,
                'patterns': [
                    r'logging\.warning\(',
                    r'logger\.warning\(',
                    r'import logging\s*\n.*?logging\.warning\(',
                ],
                'gateway_interface': 'LOGGING',
                'gateway_operation': 'warning',
                'fix': 'execute_operation(GatewayInterface.LOGGING, \'warning\', message=message, **context)',
                'description': 'Direct logging.warning() call instead of Gateway LOGGING interface',
                'why_critical': 'Bypasses structured logging and Gateway routing.'
            },

            'direct_logging_debug': {
                'name': 'Direct logging.debug() Call',
                'severity': Severity.HIGH,
                'patterns': [
                    r'logging\.debug\(',
                    r'logger\.debug\(',
                    r'import logging\s*\n.*?logging\.debug\(',
                ],
                'gateway_interface': 'LOGGING',
                'gateway_operation': 'debug',
                'fix': 'execute_operation(GatewayInterface.LOGGING, \'debug\', message=message, **context)',
                'description': 'Direct logging.debug() call instead of Gateway LOGGING interface',
                'why_critical': 'Bypasses structured logging and Gateway routing.'
            },

            # HIGH: HTTP operations
            'direct_http_get': {
                'name': 'Manual HTTP GET Request',
                'severity': Severity.HIGH,
                'patterns': [
                    r'requests\.get\(',
                    r'urllib\.request\.urlopen\(',
                    r'urlopen\(',
                    r'httpx\.get\(',
                ],
                'gateway_interface': 'HTTP_CLIENT',
                'gateway_operation': 'get',
                'fix': 'response = execute_operation(GatewayInterface.HTTP_CLIENT, \'get\', url=url, timeout=5)',
                'description': 'Manual HTTP GET instead of Gateway HTTP_CLIENT interface',
                'why_critical': 'Bypasses circuit breaker, metrics, and connection pooling.'
            },

            'direct_http_post': {
                'name': 'Manual HTTP POST Request',
                'severity': Severity.HIGH,
                'patterns': [
                    r'requests\.post\(',
                    r'urllib\.request\.Request\(.*?POST',
                    r'httpx\.post\(',
                ],
                'gateway_interface': 'HTTP_CLIENT',
                'gateway_operation': 'post',
                'fix': 'response = execute_operation(GatewayInterface.HTTP_CLIENT, \'post\', url=url, data=data)',
                'description': 'Manual HTTP POST instead of Gateway HTTP_CLIENT interface',
                'why_critical': 'Bypasses circuit breaker, metrics, and connection pooling.'
            },

            'direct_http_put': {
                'name': 'Manual HTTP PUT Request',
                'severity': Severity.HIGH,
                'patterns': [
                    r'requests\.put\(',
                    r'httpx\.put\(',
                ],
                'gateway_interface': 'HTTP_CLIENT',
                'gateway_operation': 'put',
                'fix': 'response = execute_operation(GatewayInterface.HTTP_CLIENT, \'put\', url=url, data=data)',
                'description': 'Manual HTTP PUT instead of Gateway HTTP_CLIENT interface',
                'why_critical': 'Bypasses circuit breaker, metrics, and connection pooling.'
            },

            'direct_http_delete': {
                'name': 'Manual HTTP DELETE Request',
                'severity': Severity.HIGH,
                'patterns': [
                    r'requests\.delete\(',
                    r'httpx\.delete\(',
                ],
                'gateway_interface': 'HTTP_CLIENT',
                'gateway_operation': 'delete',
                'fix': 'response = execute_operation(GatewayInterface.HTTP_CLIENT, \'delete\', url=url)',
                'description': 'Manual HTTP DELETE instead of Gateway HTTP_CLIENT interface',
                'why_critical': 'Bypasses circuit breaker, metrics, and connection pooling.'
            },

            # HIGH: Cache operations
            'direct_cache_operations': {
                'name': 'Direct Cache Import/Usage',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from cache\.cache_core import',
                    r'from cache import cache_get',
                    r'from cache import cache_set',
                    r'import cache\.cache_core',
                ],
                'gateway_interface': 'CACHE',
                'gateway_operation': 'get/set/delete',
                'fix': 'Use execute_operation(GatewayInterface.CACHE, \'operation\', key=key, value=value)',
                'description': 'Direct cache import bypasses Gateway routing',
                'why_critical': 'Violates UG-ISP architecture, bypasses ISP (Gateway) routing.'
            },

            # MEDIUM: JSON operations
            'json_loads': {
                'name': 'Manual JSON Parsing',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'json\.loads\(',
                    r'import json\s+.*?json\.loads\(',
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'parse_json',
                'fix': 'data = execute_operation(GatewayInterface.UTILITY, \'parse_json\', json_string=data)',
                'description': 'Manual JSON parsing instead of Gateway UTILITY interface',
                'why_critical': 'Misses caching and error handling benefits.'
            },

            'json_dumps': {
                'name': 'Manual JSON Serialization',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'json\.dumps\(',
                    r'import json\s+.*?json\.dumps\(',
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'format_response',
                'fix': 'json_str = execute_operation(GatewayInterface.UTILITY, \'format_response\', data=obj)',
                'description': 'Manual JSON serialization instead of Gateway UTILITY interface',
                'why_critical': 'Misses standardized formatting.'
            },

            # MEDIUM: Hash operations
            'direct_hashing': {
                'name': 'Manual Hash Generation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'hashlib\.md5\(',
                    r'hashlib\.sha256\(',
                    r'hashlib\.sha512\(',
                    r'import hashlib\s+.*?hashlib\.',
                ],
                'gateway_interface': 'SECURITY',
                'gateway_operation': 'hash_data',
                'fix': 'hash_val = execute_operation(GatewayInterface.SECURITY, \'hash_data\', data=data, algorithm=\'sha256\')',
                'description': 'Manual hash generation instead of Gateway SECURITY interface',
                'why_critical': 'Inconsistent hashing, potential security issues.'
            },

            # MEDIUM: Validation operations
            'direct_string_validation': {
                'name': 'Manual String Validation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'if\s+len\(.*?\)\s*[<>]=?\s*\d+:',  # Manual length checks
                    r'if\s+not\s+.*?\.strip\(\):',  # Manual empty checks
                ],
                'gateway_interface': 'SECURITY',
                'gateway_operation': 'validate_string',
                'fix': 'is_valid = execute_operation(GatewayInterface.SECURITY, \'validate_string\', value=value, min_length=1, max_length=1000)',
                'description': 'Manual string validation instead of Gateway SECURITY interface',
                'why_critical': 'Inconsistent validation, potential security vulnerabilities.'
            },

            # MEDIUM: UUID generation
            'direct_uuid_generation': {
                'name': 'Manual UUID Generation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'uuid\.uuid4\(',
                    r'import uuid\s+.*?uuid\.uuid4\(',
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'generate_uuid',
                'fix': 'unique_id = execute_operation(GatewayInterface.UTILITY, \'generate_uuid\')',
                'description': 'Manual UUID generation instead of Gateway UTILITY interface',
                'why_critical': 'Inconsistent ID generation patterns.'
            },

            # HIGH: Cross-interface imports (CRITICAL architecture violation)
            'cross_interface_import': {
                'name': 'Cross-Interface Direct Import',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from cache\.cache_core import',
                    r'from logging\.logging_core import',
                    r'from security\.security_core import',
                    r'from utility\.utility_core import',
                    r'from singleton\.singleton_core import',
                    r'from http_client\.http_client_core import',
                    r'from websocket\.websocket_core import',
                    r'from circuit_breaker\.circuit_breaker_core import',
                    r'from config\.config_core import',
                ],
                'gateway_interface': 'N/A',
                'gateway_operation': 'N/A',
                'fix': 'Remove direct import. Use execute_operation(GatewayInterface.INTERFACE, \'operation\', **kwargs)',
                'description': 'Direct import across interfaces bypasses Gateway ISP routing',
                'why_critical': 'CRITICAL: Violates UG-ISP architecture, breaks network topology, creates dependencies that violate isolation.'
            },

            # HIGH: Convenience wrapper imports
            'convenience_wrapper_import': {
                'name': 'Gateway Convenience Wrapper Import',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from EE import cache_get, cache_set',
                    r'from EE import log_info, log_error',
                    r'from EE import debug_log',
                    r'from gateway\.wrappers\.gateway_wrappers_cache import',
                    r'from gateway\.wrappers\.gateway_wrappers_logging import',
                ],
                'gateway_interface': 'N/A',
                'gateway_operation': 'N/A',
                'fix': 'Remove wrapper imports. Use from EE import execute_operation, GatewayInterface only',
                'description': 'Importing Gateway convenience wrappers bypasses ISP routing pattern',
                'why_critical': 'CRITICAL: Violates UG-ISP golden rule - only execute_operation and GatewayInterface should be imported from EE.'
            },

            # MEDIUM: Print statements (should use logging)
            'print_statement': {
                'name': 'Print Statement for Logging',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'print\(.*\[.*DEBUG.*\]',
                    r'print\(.*\[.*INFO.*\]',
                    r'print\(.*\[.*ERROR.*\]',
                    r'print\(.*file=sys\.stderr',
                ],
                'gateway_interface': 'LOGGING',
                'gateway_operation': 'info/error/debug',
                'fix': 'execute_operation(GatewayInterface.LOGGING, \'info\', message=message)',
                'description': 'Print statement used for logging instead of Gateway LOGGING interface',
                'why_critical': 'Bypasses structured logging, breaks CloudWatch integration.'
            },

            # MEDIUM: Configuration access
            'direct_config_access': {
                'name': 'Direct Environment Variable Access',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'os\.environ\.get\(',
                    r'os\.getenv\(',
                    r'import os\s+.*?os\.environ',
                ],
                'gateway_interface': 'CONFIG',
                'gateway_operation': 'get',
                'fix': 'value = execute_operation(GatewayInterface.CONFIG, \'get\', key=\'PARAM_NAME\')',
                'description': 'Direct environment variable access instead of Gateway CONFIG interface',
                'why_critical': 'Bypasses SSM integration and config management.'
            },

            # MEDIUM: WebSocket operations
            'direct_websocket': {
                'name': 'Direct WebSocket Import/Usage',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from websocket\.websocket_core import',
                    r'import websocket\.client',
                    r'websocket\.WebSocketApp',
                ],
                'gateway_interface': 'WEBSOCKET',
                'gateway_operation': 'connect/send/receive',
                'fix': 'Use execute_operation(GatewayInterface.WEBSOCKET, \'operation\', **kwargs)',
                'description': 'Direct WebSocket usage instead of Gateway WEBSOCKET interface',
                'why_critical': 'Bypasses connection management and metrics.'
            },

            # CRITICAL: Singleton direct access
            'direct_singleton_access': {
                'name': 'Direct Singleton Manager Access',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'from singleton\.singleton_manager import',
                    r'from singleton\.singleton_core import',
                    r'get_singleton_manager\(\)',
                    r'SingletonCore\(',
                ],
                'gateway_interface': 'SINGLETON',
                'gateway_operation': 'get/set/has',
                'fix': 'Use execute_operation(GatewayInterface.SINGLETON, \'operation\', name=name, value=value)',
                'description': 'Direct singleton access bypasses Gateway routing',
                'why_critical': 'Violates UG-ISP architecture, breaks isolation.'
            },

            # HIGH: Metrics operations
            'direct_metrics': {
                'name': 'Direct CloudWatch Metrics Import',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from metrics\.metrics_core import',
                    r'import boto3\.client\([\'"]cloudwatch[\'"]',
                ],
                'gateway_interface': 'METRICS',
                'gateway_operation': 'put/increment/gauge',
                'fix': 'Use execute_operation(GatewayInterface.METRICS, \'operation\', **kwargs)',
                'description': 'Direct metrics import instead of Gateway METRICS interface',
                'why_critical': 'Bypasses metrics aggregation and formatting.'
            },

            # EE SPECIFIC PATTERNS
            'direct_object_pool_import': {
                'name': 'Direct Object Pool Import',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from object_pool\.object_pool import',
                ],
                'gateway_interface': 'OBJECT_POOL',
                'gateway_operation': 'acquire',
                'fix': 'Use execute_operation(GatewayInterface.OBJECT_POOL, \'acquire\', name=pool_name)',
                'description': 'Direct object pool import bypasses gateway',
                'why_critical': 'Bypasses Gateway routing, violates UG-ISP architecture.'
            },

            'direct_plugin_import': {
                'name': 'Direct Plugin Import',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'from plugins\.plugins import',
                ],
                'gateway_interface': 'PLUGINS',
                'gateway_operation': 'load',
                'fix': 'Use execute_operation(GatewayInterface.PLUGINS, \'load\', name=plugin_name)',
                'description': 'Direct plugin import bypasses gateway',
                'why_critical': 'Bypasses Gateway routing, inconsistent plugin loading.'
            },

            'direct_http_client_import': {
                'name': 'Direct HTTP Client Import',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from http_client\.http_client import',
                ],
                'gateway_interface': 'HTTP_CLIENT',
                'gateway_operation': 'get',
                'fix': 'Use execute_operation(GatewayInterface.HTTP_CLIENT, \'get\', url=url)',
                'description': 'Direct HTTP client import bypasses gateway',
                'why_critical': 'Bypasses circuit breaker, metrics, and connection pooling.'
            },

            'direct_redis_import': {
                'name': 'Direct Redis Client Import',
                'severity': Severity.HIGH,
                'patterns': [
                    r'from network\.redis_client import',
                ],
                'gateway_interface': 'NETWORK',
                'gateway_operation': 'redis_get',
                'fix': 'Use execute_operation(GatewayInterface.NETWORK, \'redis_get\', key=key)',
                'description': 'Direct Redis client import bypasses gateway',
                'why_critical': 'Bypasses Gateway routing, violates UG-ISP architecture.'
            },

            # LOW: Dictionary operations
            'safe_get_pattern': {
                'name': 'Manual Safe Dictionary Get',
                'severity': Severity.LOW,
                'patterns': [
                    r'\.get\([^)]*,\s*None\)',  # dict.get(key, None)
                    r'if\s+.*?\s+in\s+.*?:',  # manual key check
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'safe_get',
                'fix': 'value = execute_operation(GatewayInterface.UTILITY, \'safe_get\', dictionary=data, key=key, default=None)',
                'description': 'Manual safe dictionary get instead of Gateway UTILITY interface',
                'why_critical': 'Inconsistent error handling patterns.'
            },

            # MEDIUM: Data sanitization
            'direct_data_sanitize': {
                'name': 'Manual Data Sanitization',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'\.replace\(["\']<script["\']',
                    r'\.replace\(["\']</script>["\']',
                    r're\.sub\(.*?script',
                ],
                'gateway_interface': 'SECURITY',
                'gateway_operation': 'sanitize_input',
                'fix': 'clean = execute_operation(GatewayInterface.SECURITY, \'sanitize_input\', input_data=user_input)',
                'description': 'Manual data sanitization instead of Gateway SECURITY interface',
                'why_critical': 'Incomplete sanitization, security vulnerability.'
            },

            # LOW: Time operations
            'direct_time_operations': {
                'name': 'Manual Time Operations',
                'severity': Severity.LOW,
                'patterns': [
                    r'time\.time\(\)',
                    r'time\.sleep\(',
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'get_timestamp',
                'fix': 'timestamp = execute_operation(GatewayInterface.UTILITY, \'get_timestamp\')',
                'description': 'Manual time operations instead of Gateway UTILITY interface',
                'why_critical': 'Inconsistent timestamp handling.'
            },

            # CRITICAL: Bare except
            'bare_except': {
                'name': 'Bare except Clause',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'except\s*:\s*$',  # Bare except
                    r'except\s*:\s*\w+',  # Bare except with code
                ],
                'gateway_interface': None,
                'gateway_operation': None,
                'fix': 'Use specific exception types: except Exception as e:',
                'description': 'Bare except catches all exceptions including SystemExit',
                'why_critical': 'CRITICAL: Catches SystemExit/KeyboardInterrupt, breaks Lambda lifecycle.'
            },

            'broad_exception': {
                'name': 'Broad Exception Catch Without Re-raise',
                'severity': Severity.HIGH,
                'patterns': [
                    r'except\s+Exception\s*:\s*\n(?!.*raise)',
                    r'except\s+Exception\s+as\s+\w+\s*:\s*\n(?!.*raise)',
                ],
                'gateway_interface': None,
                'gateway_operation': None,
                'fix': 'Either re-raise with "raise" or use specific exception type',
                'description': 'Catching Exception without re-raise can hide errors',
                'why_critical': 'Silences errors, makes debugging impossible.'
            },

            # NEW: Environment Variable Access
            'os_environ_direct': {
                'name': 'Direct os.environ Access',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'os\.environ\[',
                    r'os\.getenv\(',
                    r'import os\s+.*?os\.environ\[',
                ],
                'gateway_interface': 'CONFIG',
                'gateway_operation': 'get',
                'fix': 'value = execute_operation(GatewayInterface.CONFIG, "get", key="ENV_VAR", default=None)',
                'description': 'Direct environment variable access instead of Gateway CONFIG',
                'why_critical': 'Bypasses SSM integration and config management.'
            },

            # NEW: SQL Query Patterns
            'sql_query_string': {
                'name': 'Manual SQL Query String Construction',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'SELECT\s+.*?\+.*?FROM',
                    r'f["\'].*?SELECT.*?\{.*?\}.*?FROM',
                    r'["\'].*?SELECT.*?\{.*?\}.*?WHERE.*?\{',
                ],
                'gateway_interface': None,
                'gateway_operation': None,
                'fix': 'Use parameterized queries to prevent SQL injection',
                'description': 'SQL query constructed with string concatenation (security risk)',
                'why_critical': 'CRITICAL: SQL injection vulnerability, security breach risk.'
            },

            # NEW: Hash Patterns (enhanced existing)
            'manual_hashing_md5': {
                'name': 'Manual MD5 Hash Generation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'hashlib\.md5\(',
                    r'import hashlib\s+.*?md5\(',
                ],
                'gateway_interface': 'SECURITY',
                'gateway_operation': 'hash',
                'fix': 'hashed = execute_operation(GatewayInterface.SECURITY, "hash", data=data, algorithm="sha256")',
                'description': 'Manual MD5 hash generation (weak algorithm) instead of Gateway SECURITY',
                'why_critical': 'MD5 is cryptographically broken, use SHA256+.'
            },

            'manual_hashing_sha1': {
                'name': 'Manual SHA1 Hash Generation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'hashlib\.sha1\(',
                    r'import hashlib\s+.*?sha1\(',
                ],
                'gateway_interface': 'SECURITY',
                'gateway_operation': 'hash',
                'fix': 'hashed = execute_operation(GatewayInterface.SECURITY, "hash", data=data, algorithm="sha256")',
                'description': 'Manual SHA1 hash generation (weak algorithm) instead of Gateway SECURITY',
                'why_critical': 'SHA1 is deprecated, use SHA256+.'
            },

            # NEW: UUID Generation (enhanced existing)
            'manual_uuid_uuid1': {
                'name': 'Manual UUID1 Generation',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'uuid\.uuid1\(',
                    r'import uuid\s+.*?uuid1\(',
                ],
                'gateway_interface': 'UTILITY',
                'gateway_operation': 'generate_uuid',
                'fix': 'unique_id = execute_operation(GatewayInterface.UTILITY, "generate_uuid")',
                'description': 'Manual UUID1 generation (privacy issue) instead of Gateway UTILITY',
                'why_critical': 'UUID1 exposes MAC address, use UUID4.'
            },

            # NEW: Additional Security Patterns
            'hardcoded_password': {
                'name': 'Hardcoded Password/Secret',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                ],
                'gateway_interface': 'CONFIG',
                'gateway_operation': 'get',
                'fix': 'secret = execute_operation(GatewayInterface.CONFIG, "get", key="SECRET_NAME")',
                'description': 'Hardcoded secrets instead of secure config retrieval',
                'why_critical': 'CRITICAL: Secrets exposed in source code, security breach.'
            },

            'eval_or_exec': {
                'name': 'Direct eval() or exec() Call',
                'severity': Severity.CRITICAL,
                'patterns': [
                    r'\beval\(',
                    r'\bexec\(',
                ],
                'gateway_interface': None,
                'gateway_operation': None,
                'fix': 'Remove eval/exec. Use proper data structures or Gateway operations.',
                'description': 'Direct eval/exec allows arbitrary code execution',
                'why_critical': 'CRITICAL: Code injection vulnerability, arbitrary execution.'
            },

            # NEW: Additional Code Quality Patterns
            'global_variable': {
                'name': 'Global Variable Declaration',
                'severity': Severity.MEDIUM,
                'patterns': [
                    r'^[a-z_]+\s*=\s*(?!None|True|False|\d+)',
                ],
                'gateway_interface': 'SINGLETON',
                'gateway_operation': 'set',
                'fix': 'Use execute_operation(GatewayInterface.SINGLETON, "set", name="var_name", value=value)',
                'description': 'Global variable instead of Gateway SINGLETON',
                'why_critical': 'Breaks isolation, makes testing impossible.'
            },

            # NEW: Type Hints Missing
            'missing_type_hints': {
                'name': 'Function Missing Type Hints',
                'severity': Severity.LOW,
                'patterns': [
                    r'def\s+\w+\([^)]*\):(?!\s*->)',
                ],
                'gateway_interface': None,
                'gateway_operation': None,
                'fix': 'Add type hints: def function(param: str) -> dict:',
                'description': 'Function missing type hints',
                'why_critical': 'Reduced code clarity, no static type checking.'
            },
        }

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Compile all regex patterns for efficient matching.

        Returns:
            Dict mapping pattern categories to compiled regex patterns
        """
        compiled = {}
        for category, pattern_data in self.patterns.items():
            compiled[category] = [re.compile(pattern, re.MULTILINE | re.DOTALL)
                                for pattern in pattern_data['patterns']]
        return compiled

    def scan_file(self, file_path: str, file_content: str = None) -> List[PatternMatch]:
        """
        Scan a single file for all custom implementation patterns.

        Args:
            file_path: Path to file to scan
            file_content: Optional file content (if already loaded)

        Returns:
            List of PatternMatch objects representing violations found
        """
        if file_content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                return []

        violations = []
        lines = file_content.split('\n')

        for category, compiled_patterns in self.compiled_patterns.items():
            pattern_data = self.patterns[category]

            for pattern in compiled_patterns:
                # Check each line
                for line_num, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        # Get context lines
                        start_ctx = max(0, line_num - 2)
                        end_ctx = min(len(lines), line_num + 2)
                        context = lines[start_ctx:end_ctx]

                        violation = PatternMatch(
                            file_path=file_path,
                            line_number=line_num,
                            pattern_name=pattern_data['name'],
                            severity=pattern_data['severity'],
                            found_code=line.strip(),
                            gateway_interface=pattern_data['gateway_interface'] or 'N/A',
                            gateway_operation=pattern_data['gateway_operation'] or 'N/A',
                            fix_pattern=pattern_data['fix'],
                            description=pattern_data['description'],
                            context_lines=context
                        )
                        violations.append(violation)

        return violations

    def generate_fix(self, violation: PatternMatch) -> str:
        """
        Generate specific fix code for a violation.

        Args:
            violation: PatternMatch object

        Returns:
            String containing fix code
        """
        fix_template = f"""
# VIOLATION: {violation.pattern_name}
# Severity: {violation.severity.value}
# Found: {violation.found_code}

# FIX:
{violation.fix_pattern}

# WHY THIS MATTERS:
# {violation.description}
"""
        return fix_template

    def generate_report(self, violations: List[PatternMatch], output_format: str = 'markdown') -> str:
        """
        Generate detailed violation report.

        Args:
            violations: List of PatternMatch objects
            output_format: 'markdown' or 'json'

        Returns:
            Formatted report string
        """
        if output_format == 'json':
            import json
            return json.dumps([
                {
                    'file_path': v.file_path,
                    'line_number': v.line_number,
                    'pattern_name': v.pattern_name,
                    'severity': v.severity.value,
                    'found_code': v.found_code,
                    'gateway_interface': v.gateway_interface,
                    'gateway_operation': v.gateway_operation,
                    'fix_pattern': v.fix_pattern,
                    'description': v.description,
                }
                for v in violations
            ], indent=2)

        # Markdown format (default)
        if not violations:
            return "# Custom Implementation Violation Report\n\n**No violations found. Code is UG-ISP compliant!**\n"

        # Sort by severity and file
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        sorted_violations = sorted(violations, key=lambda v: (severity_order[v.severity], v.file_path, v.line_number))

        report = "# EE Custom Implementation Violation Report\n\n"
        report += f"**Total Violations:** {len(violations)}\n\n"

        # Group by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            sev_violations = [v for v in sorted_violations if v.severity == severity]
            if not sev_violations:
                continue

            report += f"## {severity.value} Severity ({len(sev_violations)})\n\n"

            for v in sev_violations:
                report += f"### {v.file_path}:{v.line_number}\n"
                report += f"**Pattern:** {v.pattern_name}\n"
                report += f"**Found:** `{v.found_code}`\n"
                report += f"**Gateway Interface:** `{v.gateway_interface}`\n"
                report += f"**Gateway Operation:** `{v.gateway_operation}`\n"
                report += f"**Description:** {v.description}\n\n"
                report += f"**Fix:**\n```python\n{v.fix_pattern}\n```\n\n"

                if v.context_lines:
                    report += f"**Context:**\n```python\n"
                    for i, ctx_line in enumerate(v.context_lines):
                        line_num = v.line_number - 2 + i
                        marker = ">>>" if line_num == v.line_number else "   "
                        report += f"{marker} {line_num}: {ctx_line}\n"
                    report += "```\n\n"

        return report

    def get_violation_summary(self, violations: List[PatternMatch]) -> Dict[str, Any]:
        """
        Generate summary statistics for violations.

        Args:
            violations: List of PatternMatch objects

        Returns:
            Dict containing summary statistics
        """
        summary = {
            'total_violations': len(violations),
            'by_severity': {},
            'by_pattern': {},
            'by_file': {},
        }

        for v in violations:
            # Count by severity
            sev = v.severity.value
            summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1

            # Count by pattern
            pattern = v.pattern_name
            summary['by_pattern'][pattern] = summary['by_pattern'].get(pattern, 0) + 1

            # Count by file
            file_path = v.file_path
            summary['by_file'][file_path] = summary['by_file'].get(file_path, 0) + 1

        return summary


def scan_directory(directory: str, pattern_matcher: CustomImplementationPatternMatcher = None) -> List[PatternMatch]:
    """
    Scan all Python files in a directory for custom implementations.

    Args:
        directory: Directory path to scan
        pattern_matcher: Optional CustomImplementationPatternMatcher instance

    Returns:
        List of all PatternMatch objects found
    """
    import os

    if pattern_matcher is None:
        pattern_matcher = CustomImplementationPatternMatcher()

    all_violations = []

    for root, dirs, files in os.walk(directory):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'node_modules', '.venv']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                violations = pattern_matcher.scan_file(file_path)
                all_violations.extend(violations)

    return all_violations


# EE-specific custom patterns constant for external use
EE_CUSTOM_IMPL_PATTERNS = {
    "direct_object_pool_import": {
        "pattern": r"from object_pool\.object_pool import",
        "gateway_interface": "OBJECT_POOL",
        "gateway_operation": "acquire",
        "severity": Severity.HIGH,
        "description": "Direct object pool import bypasses gateway",
    },
    "direct_plugin_import": {
        "pattern": r"from plugins\.plugins import",
        "gateway_interface": "PLUGINS",
        "gateway_operation": "load",
        "severity": Severity.MEDIUM,
        "description": "Direct plugin import bypasses gateway",
    },
    "direct_http_import": {
        "pattern": r"from http_client\.http_client import",
        "gateway_interface": "HTTP_CLIENT",
        "gateway_operation": "get",
        "severity": Severity.HIGH,
        "description": "Direct HTTP client import bypasses gateway",
    },
    "direct_redis_import": {
        "pattern": r"from network\.redis_client import",
        "gateway_interface": "NETWORK",
        "gateway_operation": "redis_get",
        "severity": Severity.HIGH,
        "description": "Direct Redis client import bypasses gateway",
    },
}


# Main entry point for standalone usage
if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python custom_impl_patterns.py <file_or_directory> [output_format]")
        print("Example: python custom_impl_patterns.py D:\\Code\\EE\\src markdown")
        sys.exit(1)

    target = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'markdown'

    matcher = CustomImplementationPatternMatcher()

    if os.path.isfile(target):
        violations = matcher.scan_file(target)
    else:
        violations = scan_directory(target, matcher)

    report = matcher.generate_report(violations, output_format)
    print(report)

    # Print summary
    summary = matcher.get_violation_summary(violations)
    print("\n## Summary")
    print(f"Total Violations: {summary['total_violations']}")
    print(f"By Severity: {summary['by_severity']}")
    print(f"Top Patterns: {dict(sorted(summary['by_pattern'].items(), key=lambda x: x[1], reverse=True)[:5])}")
