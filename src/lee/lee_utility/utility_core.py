"""utility/utility_core.py
Version: 2025-12-21_1
Purpose: Core utility manager with data operations and validation
License: Apache 2.0
"""

import logging
import os
import subprocess
import time
import uuid
from collections import deque
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_config.constants import UTILITY_CACHE_TTL
from lee.lee_utility.utility_types import UtilityMetrics

logger = logging.getLogger(__name__)


class SharedUtilityCore:  # pylint: disable=R0902
    """Core utility manager with data operations, validation, and performance tracking.

    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_utility_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    - SUGA-ISP: All debug operations via Gateway.execute_operation()
    """

    def __init__(self):
        self._metrics = {}
        self._cache_enabled = True
        self._cache_ttl = UTILITY_CACHE_TTL
        self._id_pool = []
        self._json_cache = {}
        self._json_cache_order = []
        self._max_json_cache_size = 100  # Prevent unbounded growth
        self._stats = {
            "template_hits": 0,
            "template_fallbacks": 0,
            "cache_optimizations": 0,
            "id_pool_reuse": 0,
            "lugs_integrations": 0,
            "templates_rendered": 0,
            "configs_retrieved": 0,
        }

        # Rate limiting (1000 ops/sec)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0

    def _check_rate_limit(self) -> bool:
        """Check rate limit (1000 ops/sec)."""
        now = time.time() * 1000

        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()

        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False

        self._rate_limiter.append(now)
        return True

    # === TRACKING ===

    def _start_operation_tracking(self, operation_type: str):
        """Start tracking an operation."""
        if not self._check_rate_limit():
            return

        if operation_type not in self._metrics:
            self._metrics[operation_type] = UtilityMetrics(operation_type=operation_type)

    def _complete_operation_tracking(self, operation_type: str,  # pylint: disable=R0913
                                    duration_ms: float, success: bool = True,
                                    cache_hit: bool = False, used_template: bool = False):
        """Complete tracking for an operation."""
        if not self._check_rate_limit():
            return

        metrics = self._metrics.get(operation_type)
        if not metrics:
            return
        metrics.call_count += 1

        if success:
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
        else:
            metrics.error_count += 1

        if cache_hit:
            metrics.cache_hits += 1
        elif operation_type in ["parse_json", "parse_json_safely"]:
            metrics.cache_misses += 1

        if used_template:
            metrics.template_usage += 1
            self._stats["template_hits"] += 1

    # === UUID AND TIMESTAMP ===

    def generate_uuid(self, correlation_id: str = None) -> str:
        """Generate UUID with pool optimization.

        Reuses UUIDs from internal pool when available, generates new ones otherwise.
        Uses rate limiting to prevent abuse (1000 ops/sec).

        Args:
            correlation_id: Optional correlation ID for tracking. Auto-generated if None.

        Returns:
            UUID string (36 characters, standard format).

        Rate Limiting:
            Enforces 1000 operations per second maximum.
        """

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="Rate limit exceeded in generate_uuid()")
            return str(uuid.uuid4())
        if self._id_pool:
            self._stats["id_pool_reuse"] += 1
            uuid_val = self._id_pool.pop()
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="UUID from pool", pool_size=len(self._id_pool))
            return uuid_val

        uuid_val = str(uuid.uuid4())
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="UUID generated", uuid_val=uuid_val)
        return uuid_val

    def get_timestamp_iso(self, correlation_id: str = None) -> str:
        """Get current timestamp as ISO string."""

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Timestamp generated", timestamp=timestamp)
        return timestamp

    def get_timestamp_numeric(self, correlation_id: str = None) -> float:
        """Get current timestamp as Unix timestamp (seconds since epoch).

        Args:
            correlation_id: Optional correlation_id for tracking

        Returns:
            Current timestamp as float (Unix timestamp in seconds).
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        timestamp = time.time()
        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Numeric timestamp generated", timestamp=timestamp)
        return timestamp

    def get_timestamp(self, correlation_id: str = None) -> str:
        """Get current timestamp as ISO string.

        Convenience method that delegates to get_timestamp_iso.

        Args:
            correlation_id: Optional correlation ID for tracking

        Returns:
            Current timestamp as ISO 8601 string
        """
        return self.get_timestamp_iso(correlation_id)

    def generate_correlation_id_impl(self, prefix: Optional[str] = None,
                                     correlation_id: str = None) -> str:
        """Generate correlation ID with optional prefix.

        Creates a unique correlation ID for request tracking across distributed systems.
        Wraps generate_uuid() with optional prefix for domain identification.

        Args:
            prefix: Optional prefix for domain/organization identification (e.g., "alex", "ha").
            correlation_id: Optional correlation ID for tracking. Auto-generated if None.

        Returns:
            Correlation ID string. If prefix provided, returns "{prefix}_{uuid}".
            Otherwise returns UUID string.

        Examples:
            >>> generate_correlation_id_impl(prefix="alex")
            "alex_550e8400-e29b-41d4-a716-446655440000"
            >>> generate_correlation_id_impl()
            "550e8400-e29b-41d4-a716-446655440000"
        """

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        base_id = self.generate_uuid(correlation_id)
        if prefix:
            result = f"{prefix}_{base_id}"
            execute_operation(GatewayInterface.DEBUG, "log",
                            message="Correlation ID with prefix",
                            prefix=prefix, result_length=len(result))

        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Correlation ID generated",
                        result_length=len(base_id))
        return base_id

    # === TEMPLATE RENDERING ===

    def render_template_impl(self, template: dict, data: dict,
                            correlation_id: str = None, **_kwargs) -> dict:
        """Render template with placeholder substitution.

        Replaces {placeholder} patterns in template dictionary with values from data.
        Supports nested structures (lists, dicts) by JSON serialization.

        Args:
            template: Template dictionary with {placeholder} patterns.
            data: Dictionary mapping placeholder names to values.
            correlation_id: Optional correlation ID for tracking. Auto-generated if None.
            **kwargs: Additional parameters (unused, for interface compatibility).

        Returns:
            Rendered template dictionary with placeholders replaced by values.

        Behavior:
            - Adds "message_id" to data if not present (generates correlation ID)
            - Replaces all {key} patterns with corresponding values from data
            - Converts complex values (lists, dicts) to JSON strings
            - Converts None to empty string
            - If rate limit exceeded or rendering fails, returns original template

        Example:
            >>> template = {"message": "Hello {name}", "count": 1}
            >>> data = {"name": "World"}
            >>> render_template_impl(template, data)
            {"message": "Hello World", "count": 1}
        """
        """Render template with {placeholder} substitution.

        Args:
            template: Template dictionary with {placeholder} patterns.
            data: Dictionary mapping placeholder names to values.
            correlation_id: Optional correlation ID for tracking. Auto-generated if None.
            **kwargs: Additional parameters (unused, for interface compatibility).

        Returns:
            Rendered template dictionary with placeholders replaced by values.
        """

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Rate limit exceeded in render_template_impl()")
            return template

        execute_operation(GatewayInterface.DEBUG, "log",
                        corr_id=correlation_id, scope="UTILITY_MANAGER",
                        message="Rendering template", placeholder_count=len(data))

        with execute_operation(GatewayInterface.DEBUG, "timing",
                             corr_id=correlation_id, scope="UTILITY_MANAGER",
                             op_name="render_template") as _:
            try:
                if "message_id" not in data:
                    data["message_id"] = self.generate_correlation_id_impl(correlation_id=correlation_id)

                # Optimized template rendering using recursive traversal
                # Avoids JSON serialization/deserialization overhead
                def deep_replace(obj: Any, replacements: dict) -> Any:
                    """Recursively replace {key} placeholders in nested structures.

                    Args:
                        obj: Template object (dict, list, or primitive)
                        replacements: Dictionary mapping placeholder names to values

                    Returns:
                        New object with placeholders replaced
                    """
                    if isinstance(obj, dict):
                        result = {}
                        for key, value in obj.items():
                            # Recursively replace in both keys and values
                            new_key = deep_replace(key, replacements)
                            new_value = deep_replace(value, replacements)
                            result[new_key] = new_value
                        return result
                    if isinstance(obj, list):
                        return [deep_replace(item, replacements) for item in obj]
                    if isinstance(obj, str):
                        # Replace all {placeholder} patterns in string
                        result = obj
                        for placeholder_name, value in replacements.items():
                            placeholder = f"{{{placeholder_name}}}"
                            # Handle None values
                            replacement_value = "" if value is None else value
                            result = result.replace(placeholder, str(replacement_value))
                        return result
                    return obj

                result = deep_replace(template, data)

                self._stats["templates_rendered"] += 1
                execute_operation(GatewayInterface.DEBUG, "log",
                                corr_id=correlation_id, scope="UTILITY_MANAGER",
                                message="Template rendered successfully")

                return result

            except (ValueError, TypeError, KeyError) as e:
                logger.error(f"Template rendering failed: {e}")
                return template
            except (AttributeError, RuntimeError, OSError) as e:
                logger.error(f"Template rendering error: {e}")
                return template

    # === CONFIG RETRIEVAL ===

    def config_get_impl(self, key: str, default=None,
                       correlation_id: str = None, **_kwargs) -> Any:
        """Get typed configuration value from environment.

        Retrieves environment variable with optional type conversion based on
        the type of the default parameter.

        Args:
            key: Environment variable name.
            default: Default value if key not found. Determines return type:
                - If bool: Converts "true", "1", "yes", "on" (case-insensitive) to True
                - If int: Converts to integer
                - If float: Converts to float
                - Otherwise: Returns string value as-is
            correlation_id: Optional correlation ID for tracking. Auto-generated if None.
            **kwargs: Additional parameters (unused, for interface compatibility).

        Returns:
            Environment variable value, converted to match default's type.
            If key not found and default provided, returns default.
            If key not found and default is None, returns None.

        Rate Limiting:
            Enforces 1000 operations per second maximum.

        Examples:
            >>> os.environ["DEBUG"] = "true"
            >>> config_get_impl("DEBUG", default=False)
            True
            >>> os.environ["PORT"] = "8080"
            >>> config_get_impl("PORT", default=8000)
            8080
            >>> config_get_impl("MISSING", default="default_value")
            "default_value"
        """

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Rate limit exceeded in config_get_impl()")
            return default

        value = os.getenv(key)

        if value is None:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Config not found, using default",
                            key=key, has_default=default is not None)
            return default

        if default is None:
            self._stats["configs_retrieved"] += 1
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Config retrieved as string", key=key)
            return value

        try:
            if isinstance(default, bool):
                result = value.lower() in ("true", "1", "yes", "on")
            elif isinstance(default, int):
                result = int(value)
            elif isinstance(default, float):
                result = float(value)
            else:
                result = value

            self._stats["configs_retrieved"] += 1
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Config retrieved and converted",
                            key=key, result_type=type(result).__name__)
            return result

        except (ValueError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                            corr_id=correlation_id, scope="UTILITY_MANAGER",
                            message="Config conversion failed, using default",
                            key=key, error=str(e))
            logger.debug("Config conversion failed for %s=%s, using default=%s", key, value, default)
            return default

    # === SAFE SUBPROCESS ===

    def safe_subprocess_run_implementation(  # pylint: disable=R0913,R0914,R0912,R0915,R0917
            self, command: list, timeout: int = 30,
            capture_output: bool = True,
            check: bool = False,
            cwd: str = None,
            env: dict = None,
            correlation_id: str = None, **_kwargs) -> dict:
        """Safely execute subprocess with comprehensive security validation.

        SECURITY:
        - NEVER uses shell=True (prevents command injection)
        - Validates NO shell metacharacters: |, &, ;, $, `, \n, \r
        - Forces list format for commands (no string parsing)
        - Sanitizes environment variables if provided
        - Logs all subprocess execution via gateway

            command: Command as list (e.g., ['python', '-m', 'pytest'])
            timeout: Timeout in seconds (default: 30)
            capture_output: Capture stdout/stderr (default: True)
            check: Raise exception on non-zero exit (default: False)
            cwd: Working directory (optional)
            env: Environment variables dict (optional, will be sanitized)
            correlation_id: Correlation ID for logging (optional)

            dict with keys:
                - stderr: str (decoded if capture_output=True)
                - returncode: int
                - success: bool

        Raises:
            ValueError: If command contains shell metacharacters
            TypeError: If command is not a list
            subprocess.TimeoutExpired: If timeout exceeded
            subprocess.CalledProcessError: If check=True and non-zero exit

        """

        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        # Validate command is a list
        if not isinstance(command, list):
            raise TypeError(
                f"command must be a list, got {type(command).__name__}. "
                "This prevents command injection via shell parsing.",
            )

        # Validate command is not empty
        if not command:
            raise ValueError("command list cannot be empty")

        # Security validation:
        # Since we use shell=False, arguments are safe.
        # Only the command name (first element) needs strict validation.
        # We validate that shell=True is NEVER used.

        # Validate command parts are strings
        for i, part in enumerate(command):
            if not isinstance(part, str):
                raise TypeError(
                    f"command[{i}] must be str, got {type(part).__name__}: {part}",
                )

        # Additional validation: command name should not contain obvious injection patterns
        # This is defense-in-depth since shell=False prevents shell injection
        command_name = command[0]
        dangerous_patterns = ["|", "&", ";", "$", "`", "\n", "\r"]
        for pattern in dangerous_patterns:
            if pattern in command_name:
                raise ValueError(
                    f"Security violation: command name contains dangerous pattern '{pattern}': {command_name}. "
                    f"This prevents command injection attacks.",
                )

        # Validate ALL command arguments (not just first element)
        # Defense-in-depth: prevent argument injection attacks
        for i, arg in enumerate(command):
            for pattern in dangerous_patterns:
                if pattern in arg:
                    raise ValueError(
                        f"Security violation: command[{i}] contains dangerous pattern '{pattern}': {arg}. "
                        f"This prevents command injection attacks.",
                    )

        # Validate and sanitize cwd parameter to prevent path traversal
        if cwd is not None:
            if not isinstance(cwd, str):
                raise TypeError(f"cwd must be str, got {type(cwd).__name__}")

            # Resolve absolute path and check for path traversal attempts
            try:
                abs_cwd = os.path.abspath(cwd)
                # Check if resolved path actually exists
                if not os.path.exists(abs_cwd):
                    raise ValueError(f"Working directory does not exist: {abs_cwd}")
                # Check if it's a directory
                if not os.path.isdir(abs_cwd):
                    raise ValueError(f"Working directory is not a directory: {abs_cwd}")
                cwd = abs_cwd
            except (OSError, ValueError) as exc:
                raise ValueError(f"Invalid working directory '{cwd}': {exc}") from exc

        # Sanitize environment variables if provided
        sanitized_env = None
        if env is not None:
            if not isinstance(env, dict):
                raise TypeError(f"env must be dict, got {type(env).__name__}")

            sanitized_env = {}
            for key, value in env.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise TypeError("env keys and values must be strings")

                # CRITICAL: Comprehensive security validation for environment variables
                # Prevents command injection via encoded characters, control chars,
                # path traversal, and dangerous patterns

                # 1. Validate environment variable key (defense against path traversal)
                # Only allow valid Python identifiers (alphanumeric + underscore, no leading digit)
                if not key.isidentifier():
                    raise ValueError(
                        f"Security violation: env variable key '{key}' is not a valid identifier. "
                        f"This prevents command injection via malformed environment variables.",
                    )

                # 2. Validate environment variable value length (prevent DoS)
                # Environment variables should be reasonably sized
                # Configurable via LEE_MAX_ENV_VALUE_LENGTH env var (default: 8192)
                MAX_ENV_VALUE_LENGTH = int(os.getenv("LEE_MAX_ENV_VALUE_LENGTH", "8192"))
                if len(value) > MAX_ENV_VALUE_LENGTH:
                    raise ValueError(
                        f"Security violation: env variable '{key}' value too long ({len(value)} chars). "
                        f"Maximum allowed: {MAX_ENV_VALUE_LENGTH} chars. This prevents DoS attacks.",
                    )

                # 3. Block ALL control characters (ord(c) < 32)
                # This prevents bypasses using encoded newlines (\x0a), tabs (\x09), etc.
                for i, char in enumerate(value):
                    if ord(char) < 32:
                        raise ValueError(
                            f"Security violation: env variable '{key}' contains control character "
                            f"at position {i} (ordinal {ord(char)}). "
                            f"This prevents command injection via encoded control characters.",
                        )

                # 4. Comprehensive dangerous pattern blocking
                # Block shell metacharacters, command separators, and dangerous constructs
                comprehensive_dangerous_patterns = [
                    # Shell metacharacters
                    "|", "&", ";", "$", "`", "\\", "(", ")", "[", "]", "{", "}",
                    # Command separators
                    "\n", "\r", "\t", "\x0b", "\x0c", "\x00",
                    # Redirection operators
                    "<", ">", "<<", ">>",
                    # Command chains
                    "&&", "||",
                    # Variable expansion patterns (Unix and Windows)
                    "${", "%", "!", "*",
                    # Command substitution
                    "$(", ")",
                    # Backticks (already in metacharacters, but explicit for clarity)
                    "`",
                    # Path traversal attempts
                    "..", "../", "..\\",
                    # NULL byte
                    "\x00",
                    # Unicode control characters (C0 and C1 control sets)
                    "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07",
                    "\x08", "\x0b", "\x0c", "\x0e", "\x0f", "\x10", "\x11",
                    "\x12", "\x13", "\x14", "\x15", "\x16", "\x17", "\x18",
                    "\x19", "\x1a", "\x1b", "\x1c", "\x1d", "\x1e", "\x1f",
                    "\x7f", "\x80", "\x81", "\x82", "\x83", "\x84", "\x85",
                    "\x86", "\x87", "\x88", "\x89", "\x8a", "\x8b", "\x8c",
                    "\x8d", "\x8e", "\x8f", "\x90", "\x91", "\x92", "\x93",
                    "\x94", "\x95", "\x96", "\x97", "\x98", "\x99", "\x9a",
                    "\x9b", "\x9c", "\x9d", "\x9e", "\x9f",
                ]

                # Check for dangerous patterns in value
                for pattern in comprehensive_dangerous_patterns:
                    if pattern in value:
                        raise ValueError(
                            f"Security violation: env variable '{key}' contains dangerous pattern '{pattern}'. "
                            f"This prevents command injection via environment variables.",
                        )

                # 5. Additional validation: check for case variations of dangerous patterns
                # Some shells may interpret patterns case-insensitively
                lowercase_value = value.lower()
                dangerous_lower = ["cmd", "powershell", "bash", "sh", "curl", "wget", "nc", "netcat"]
                for dangerous in dangerous_lower:
                    if dangerous in lowercase_value:
                        raise ValueError(
                            f"Security violation: env variable '{key}' may contain command injection attempt "
                            f"(detected '{dangerous}' in value). This prevents command execution.",
                        )

                sanitized_env[key] = value

        # Log subprocess execution (using simple logging to avoid circular dependency)
        logger.info(
            "Executing subprocess: %s (corr_id=%s, command=%s, timeout=%ds)",
            command[0],
            correlation_id,
            ' '.join(command[:3]),
            timeout,
        )

        # Execute subprocess with shell=False (CRITICAL)
        try:
            result = subprocess.run(
                command,
                shell=False,  # CRITICAL: NEVER use shell=True
                timeout=timeout,
                capture_output=capture_output,
                check=check,
                cwd=cwd,
                env=sanitized_env,
                text=True,  # Decode output as text
            )

            return {
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            logger.warning(
                "Subprocess timeout: %s (corr_id=%s, timeout=%ds)",
                command[0],
                correlation_id,
                timeout,
            )
            raise

        except subprocess.CalledProcessError as e:
            logger.warning(
                "Subprocess failed: %s (corr_id=%s, returncode=%d)",
                command[0],
                correlation_id,
                e.returncode,
            )
            raise

        except (ValueError, TypeError, KeyError) as e:
            logger.error(
                "Subprocess exception: %s (corr_id=%s, error=%s: %s)",
                command[0],
                correlation_id,
                type(e).__name__,
                e,
            )
            raise
        except (OSError, TimeoutError, MemoryError) as e:
            logger.error(
                "Subprocess system error: %s (corr_id=%s, error=%s: %s)",
                command[0],
                correlation_id,
                type(e).__name__,
                e,
            )
            raise


__all__ = [
    "SharedUtilityCore",
]
