"""Security Wrapper Functions

Direct access to security operations (18 functions + 2 enhanced validation).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import security

    # Validate token
    is_valid = security.validate_token(token='eyJhbG...')

    # Validate string
    security.validate_string(value='input', min_length=1, max_length=1000)

    # Enhanced input validation (NEW)
    is_safe, threat_info = security.validate_string_input('<script>alert(1)</script>')
    clean = security.sanitize_input('<script>alert(1)</script>')

    # Generate correlation ID
    corr_id = security.generate_correlation_id()

    # Hash data
    hashed = security.hash_data(data='password')

    # Verify hash
    is_valid = security.verify_hash(data='password', hashed=hashed)

    # Sanitize for logs
    safe = security.sanitize_for_log(log_data='Token: eyJhbG...')
"""

import logging
from typing import Any, Optional

from lee.gateway.gateway_core import GatewayInterface, execute_operation

# Import enhanced input sanitizer
try:
    from lee.lee_security.security_sanitizer import (
        InputSanitizer,
        SanitizeLevel,
        ThreatType,
    )
except ImportError:
    InputSanitizer = None
    SanitizeLevel = None
    ThreatType = None

_logger = logging.getLogger(__name__)


def validate_token(token: str, **kwargs: Any) -> bool:
    """Validate authentication token.

    Args:
        token: Token to validate
        **kwargs: Additional validation options

    Returns:
        True if token is valid, False otherwise
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token, **kwargs)


def compare_tokens(token1: str, token2: str, **kwargs: Any) -> bool:
    """Compare two tokens in constant time.

    Args:
        token1: First token
        token2: Second token
        **kwargs: Additional comparison options

    Returns:
        True if tokens match, False otherwise
    """
    return execute_operation(GatewayInterface.SECURITY, 'compare_tokens', token1=token1, token2=token2, **kwargs)


def generate_correlation_id(prefix: str = 'corr', **kwargs: Any) -> str:
    """Generate correlation ID for request tracking.

    Args:
        prefix: Prefix for correlation ID
        **kwargs: Additional generation options

    Returns:
        Correlation ID string
    """
    return execute_operation(GatewayInterface.UTILITY, 'generate_correlation_id', prefix=prefix, **kwargs)


def hash_data(data: str, **kwargs: Any) -> str:
    """Hash data using SHA-256.

    Args:
        data: Data to hash
        **kwargs: Additional hashing options

    Returns:
        Hex-encoded hash string
    """
    return execute_operation(GatewayInterface.SECURITY, 'hash', data=data, **kwargs)


def verify_hash(data: str, hashed: str, **kwargs: Any) -> bool:
    """Verify data against hash.

    Args:
        data: Original data
        hashed: Hash to verify against
        **kwargs: Additional verification options

    Returns:
        True if hash matches, False otherwise
    """
    return execute_operation(GatewayInterface.SECURITY, 'verify_hash', data=data, hashed=hashed, **kwargs)


def sanitize_input(user_input: str, **kwargs: Any) -> str:
    """Sanitize user input to prevent XSS and injection attacks.

    Args:
        user_input: Input to sanitize
        **kwargs: Additional sanitization options

    Returns:
        Sanitized input string
    """
    return execute_operation(GatewayInterface.SECURITY, 'sanitize_input', user_input=user_input, **kwargs)


def sanitize_for_log(log_data: str, **kwargs: Any) -> str:
    """Sanitize log data by redacting sensitive information.

    Args:
        log_data: Log data to sanitize
        **kwargs: Additional sanitization options

    Returns:
        Sanitized log data
    """
    return execute_operation(GatewayInterface.SECURITY, 'sanitize_log', log_data=log_data, **kwargs)


def validate_request(request: dict[str, Any], **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate HTTP request data.

    Args:
        request: Request data to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request=request, **kwargs)


def validate_string(value: str, min_length: int = 0, max_length: int = 1000, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate string input.

    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_string', value=value, min_length=min_length, max_length=max_length, **kwargs)


def validate_email(email: str, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate email address format.

    Args:
        email: Email to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_email', email=email, **kwargs)


def validate_url(url: str, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate URL format and safety.

    Args:
        url: URL to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_url', url=url, **kwargs)


def validate_cache_key(key: str, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate cache key format.

    Args:
        key: Cache key to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_cache_key', key=key, **kwargs)


def validate_ttl(ttl: float, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate TTL value.

    Args:
        ttl: TTL to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_ttl', ttl=ttl, **kwargs)


def validate_module_name(name: str, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate module name format.

    Args:
        name: Module name to validate
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_module_name', name=name, **kwargs)


def validate_number_range(value: int | float, min_val: int | float = 0, max_val: int | float = 100, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate number is within range.

    Args:
        value: Number to validate
        min_val: Minimum value
        max_val: Maximum value
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SECURITY, 'validate_number_range', value=value, min_val=min_val, max_val=max_val, **kwargs)


def validate_string_input(value: str, max_length: int = 1000, **kwargs: Any) -> tuple[bool, Optional[str]]:  # pylint: disable=too-many-return-statements,too-many-branches,too-many-locals
    """Validate string input for comprehensive security threats.

    Enhanced validation that detects:
    - XSS (Cross-Site Scripting) attacks
    - SQL injection attacks
    - Command injection attacks
    - Path traversal attacks
    - SSRF (Server-Side Request Forgery)

    Args:
        value: String to validate
        max_length: Maximum allowed length (default: 1000)
        **kwargs: Additional validation options
            - check_xss: Enable XSS detection (default: True)
            - check_sql: Enable SQL injection detection (default: True)
            - check_command: Enable command injection detection (default: True)
            - check_path: Enable path traversal detection (default: True)
            - check_ssrf: Enable SSRF detection (default: True)
            - log_failures: Log validation failures (default: True)

    Returns:
        Tuple of (is_safe, threat_info)
        - is_safe: True if input passes all security checks
        - threat_info: String describing detected threats, or None if safe

    Example:
        >>> is_safe, threat = validate_string_input('<script>alert(1)</script>')
        >>> assert not is_safe
        >>> assert 'XSS' in threat

        >>> is_safe, threat = validate_string_input("'; DROP TABLE users; --")
        >>> assert not is_safe
        >>> assert 'SQL' in threat

        >>> is_safe, threat = validate_string_input('../../../etc/passwd')
        >>> assert not is_safe
        >>> assert 'path traversal' in threat
    """
    if InputSanitizer is None:
        _logger.warning("InputSanitizer not available, using basic validation")
        # Fallback to basic validation
        if not isinstance(value, str):
            return False, "Input must be a string"
        if len(value) > max_length:
            return False, f"Input exceeds maximum length of {max_length}"
        return True, None

    # Extract validation options
    check_xss = kwargs.get('check_xss', True)
    check_sql = kwargs.get('check_sql', True)
    check_command = kwargs.get('check_command', True)
    check_path = kwargs.get('check_path', True)
    check_ssrf = kwargs.get('check_ssrf', True)
    log_failures = kwargs.get('log_failures', True)

    # Basic type validation
    if not isinstance(value, str):
        error_msg = "Input must be a string"
        if log_failures:
            _logger.warning(
                error_msg,
                extra={
                    'security_event': True,
                    'operation': 'validate_string_input',
                    'input_type': type(value).__name__
                }
            )
        return False, error_msg

    # Length validation
    if len(value) > max_length:
        error_msg = "Input exceeds maximum length of %d characters (got %d)" % (max_length, len(value))  # pylint: disable=consider-using-f-string
        if log_failures:
            _logger.warning(
                error_msg,
                extra={
                    'security_event': True,
                    'operation': 'validate_string_input',
                    'length': len(value),
                    'max_length': max_length
                }
            )
        return False, error_msg

    # Use InputSanitizer for comprehensive threat detection
    try:
        sanitizer = InputSanitizer(level=SanitizeLevel.HIGH)
        result = sanitizer.sanitize(value, context="general")

        if not result.is_safe:
            # Dictionary dispatch for threat type processing (O(1) lookup)
            # pylint: disable=consider-using-f-string
            threat_types = []
            threat_details = []

            # Threat type handlers with conditional checks
            def _handle_xss(threat):
                if check_xss:
                    return ("XSS", f"XSS pattern detected at position {threat.position}: {threat.pattern}")
                return None

            def _handle_sql(threat):
                if check_sql:
                    return ("SQL Injection", f"SQL injection pattern detected at position {threat.position}: {threat.pattern}")
                return None

            def _handle_command(threat):
                if check_command:
                    return ("Command Injection", f"Command injection pattern detected at position {threat.position}: {threat.pattern}")
                return None

            def _handle_path(threat):
                if check_path:
                    return ("Path Traversal", f"Path traversal pattern detected at position {threat.position}: {threat.pattern}")
                return None

            def _handle_ssrf(threat):
                if check_ssrf:
                    return ("SSRF", f"SSRF pattern detected at position {threat.position}: {threat.pattern}")
                return None

            # Dispatch dictionary for threat types
            _THREAT_HANDLERS = {
                ThreatType.XSS: _handle_xss,
                ThreatType.SQL_INJECTION: _handle_sql,
                ThreatType.COMMAND_INJECTION: _handle_command,
                ThreatType.PATH_TRAVERSAL: _handle_path,
                ThreatType.SSRF: _handle_ssrf,
            }

            for threat in result.threats:
                handler = _THREAT_HANDLERS.get(threat.threat_type)
                if handler:
                    result_tuple = handler(threat)
                    if result_tuple:
                        threat_types.append(result_tuple[0])
                        threat_details.append(result_tuple[1])

            if threat_types:
                error_msg = (  # pylint: disable=consider-using-f-string
                    "Security threat detected: %s. Details: %s" % (
                        ', '.join(set(threat_types)),
                        '; '.join(threat_details[:3])
                    )
                )

                if log_failures:
                    _logger.warning(
                        error_msg,
                        extra={
                            'security_event': True,
                            'operation': 'validate_string_input',
                            'threat_types': list(set(threat_types)),
                            'threat_count': len(result.threats)
                        }
                    )

                return False, error_msg

        return True, None

    except (ValueError, TypeError, AttributeError, KeyError) as e:
        # Input validation errors
        error_msg = f"Validation error: {e.__class__.__name__}: {e}"
        if log_failures:
            _logger.error(
                error_msg,
                extra={
                    'security_event': True,
                    'operation': 'validate_string_input',
                    'exception': e.__class__.__name__
                }
            )
        return False, error_msg
    except (ImportError, RuntimeError, OSError) as e:
        # System-level errors
        error_msg = f"System error during validation: {e.__class__.__name__}: {e}"
        if log_failures:
            _logger.error(
                error_msg,
                extra={
                    'security_event': True,
                    'operation': 'validate_string_input',
                    'exception': e.__class__.__name__
                }
            )
        return False, error_msg


def sanitize_input_enhanced(user_input: str, context: str = "general", **kwargs: Any) -> str:
    """Sanitize user input to prevent XSS and injection attacks (Enhanced version).

    This function provides comprehensive input sanitization using the InputSanitizer
    class, which detects and encodes dangerous content.

    Args:
        user_input: Input to sanitize
        context: Context hint (html, js, url, general)
                - html: HTML escape (prevent XSS in HTML context)
                - url: URL escape (prevent injection in URLs)
                - js: JavaScript escape (prevent XSS in JS context)
                - general: HTML escape (default, safest option)
        **kwargs: Additional sanitization options
            - level: SanitizeLevel (MEDIUM, HIGH, STRICT) - default: HIGH
            - max_length: Maximum allowed length - default: 10000

    Returns:
        Sanitized input string with dangerous content encoded

    Example:
        >>> clean = sanitize_input_enhanced('<script>alert("XSS")</script>Hello')
        >>> assert '&lt;script&gt;' in clean
        >>> assert 'Hello' in clean

        >>> clean = sanitize_input_enhanced("'; DROP TABLE users; --")
        >>> assert 'DROP TABLE' not in clean or '; DROP' in clean

    Raises:
        ValueError: If input is not a string
    """
    if InputSanitizer is None:
        _logger.warning("InputSanitizer not available, using basic sanitization")
        # Fallback to basic sanitization
        if not isinstance(user_input, str):
            raise ValueError(f"Input must be a string, got {type(user_input).__name__}")
        # Remove control characters and limit length
        max_length = kwargs.get('max_length', 10000)
        sanitized = "".join(char for char in user_input if ord(char) >= 32 or char in "\n\r\t")
        return sanitized[:max_length]

    # Basic type validation
    if not isinstance(user_input, str):
        raise ValueError(f"Input must be a string, got {type(user_input).__name__}")

    # Get sanitization level
    level = kwargs.get('level', SanitizeLevel.HIGH)
    max_length = kwargs.get('max_length', 10000)

    # Truncate if too long
    if len(user_input) > max_length:
        _logger.warning(
            "Input truncated from %d to %d characters",
            len(user_input),
            max_length,
            extra={
                'security_event': True,
                'operation': 'sanitize_input_enhanced',
                'original_length': len(user_input),
                'truncated_length': max_length
            }
        )
        user_input = user_input[:max_length]

    try:
        sanitizer = InputSanitizer(level=level)
        result = sanitizer.sanitize(user_input, context=context)

        # Log if threats were detected
        if result.threats:
            threat_types = [t.threat_type.value for t in result.threats]
            _logger.warning(
                "Threats detected and sanitized: %s",
                ', '.join(set(threat_types)),
                extra={
                    'security_event': True,
                    'operation': 'sanitize_input_enhanced',
                    'threat_types': list(set(threat_types)),
                    'threat_count': len(result.threats),
                    'encoding': result.encoding
                }
            )

        return result.sanitized

    except (ValueError, TypeError, AttributeError) as e:
        # Input sanitization errors
        _logger.error(
            "Sanitization error: %s: %s",
            e.__class__.__name__,
            e,
            extra={
                'security_event': True,
                'operation': 'sanitize_input_enhanced',
                'exception': e.__class__.__name__
            }
        )
        # Return empty string on error to be safe
        return ""
    except (ImportError, RuntimeError, OSError) as e:
        # System-level errors
        _logger.error(
            "System error during sanitization: %s: %s",
            e.__class__.__name__,
            e,
            extra={
                'security_event': True,
                'operation': 'sanitize_input_enhanced',
                'exception': e.__class__.__name__
            }
        )
        # Return empty string on error to be safe
        return ""


__all__ = [
    'compare_tokens',
    'generate_correlation_id',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    'sanitize_for_log',
    'validate_request',
    'validate_token',
    'validate_string',
    'validate_email',
    'validate_url',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
    'validate_string_input',
    'sanitize_input_enhanced',
]
