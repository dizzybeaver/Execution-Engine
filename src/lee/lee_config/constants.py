"""lee_config/constants.py

Centralized configuration constants for LEE modules.
Eliminates magic numbers and provides single source of truth for thresholds.

Version: 2026-04-01
License: Apache 2.0
"""

# ===== HTTP CLIENT CONSTANTS =====

# Default HTTP timeout in seconds
HTTP_DEFAULT_TIMEOUT = 10.0

# Long-running HTTP timeout (for slow operations) in seconds
HTTP_LONG_TIMEOUT = 60.0

# Maximum number of HTTP retry attempts
HTTP_MAX_RETRIES = 2

# Backoff factor for HTTP retries (exponential backoff)
HTTP_BACKOFF_FACTOR = 0.5

# Maximum number of HTTP redirects to follow
HTTP_MAX_REDIRECTS = 5

# ===== CACHE CONSTANTS =====

# Default cache TTL in seconds (5 minutes)
CACHE_DEFAULT_TTL = 300

# Maximum cache size in bytes (100 MB)
CACHE_MAX_BYTES = 104857600

# Maximum number of cache entries
CACHE_MAX_ENTRIES = 10000

# Cache rate limit window in milliseconds
CACHE_RATE_LIMIT_WINDOW_MS = 60000

# Cache rate limit maximum operations
CACHE_RATE_LIMIT_MAX_OPS = 1000

# Memory check interval for cache pressure (in milliseconds)
CACHE_MEMORY_CHECK_INTERVAL_MS = 5000

# Memory check sample rate (10% of operations)
CACHE_MEMORY_CHECK_SAMPLE_RATE = 0.1

# ===== STRING VALIDATION CONSTANTS =====

# Default minimum string length for validation
STRING_MIN_LENGTH = 1

# Default maximum string length for validation (10KB)
STRING_MAX_LENGTH = 10000

# Maximum string length for log messages (prevent log injection)
STRING_LOG_MAX_LENGTH = 1000

# Maximum string length for safe string conversion
STRING_CONVERSION_MAX_LENGTH = 100

# ===== UTILITY CONSTANTS =====

# Default cache TTL for utility operations (seconds)
UTILITY_CACHE_TTL = 300

# UUID version to use for UUID generation
UTILITY_UUID_VERSION = 4

# ===== NETWORK CONSTANTS =====

# WebSocket connection timeout in seconds
WEBSOCKET_CONNECT_TIMEOUT = 10.0

# WebSocket read timeout in seconds
WEBSOCKET_READ_TIMEOUT = 30.0

# WebSocket ping interval in seconds
WEBSOCKET_PING_INTERVAL = 20.0

# WebSocket ping timeout in seconds
WEBSOCKET_PING_TIMEOUT = 10.0

# ===== CIRCUIT BREAKER CONSTANTS =====

# Default failure threshold for circuit breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5

# Default recovery timeout in seconds
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60

# Default half-open max calls
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS = 3

# ===== SECURITY CONSTANTS =====

# Maximum token length for validation
SECURITY_MAX_TOKEN_LENGTH = 2048

# Maximum URL length for SSRF protection
SECURITY_MAX_URL_LENGTH = 2048

# Salt length for secure hashing
SECURITY_SALT_LENGTH = 32

# Token length for CSPRNG generation
SECURITY_TOKEN_LENGTH = 32

# ===== LOGGING CONSTANTS =====

# Maximum log buffer size for bootstrap logging
LOGGING_MAX_BUFFER_SIZE = 100

# Maximum log message length
LOGGING_MAX_MESSAGE_LENGTH = 10000

# Log sampling rate for debug logging (10%)
LOGGING_DEBUG_SAMPLE_RATE = 0.1

# ===== PERFORMANCE CONSTANTS =====

# Default sampling rate for performance profiling
PERFORMANCE_DEFAULT_SAMPLE_RATE = 0.1

# Maximum number of performance metrics to keep
PERFORMANCE_MAX_METRICS = 10000

# Resource profiling interval in milliseconds
PERFORMANCE_PROFILING_INTERVAL_MS = 1000

# ===== METADATA CONSTANTS =====

# Maximum event bus queue size
METADATA_MAX_EVENT_QUEUE_SIZE = 1000

# Event bus processing timeout in seconds
METADATA_EVENT_TIMEOUT = 5.0

# ===== TESTING CONSTANTS =====

# Default timeout for test operations
TEST_DEFAULT_TIMEOUT = 5.0

# Maximum retry attempts for test operations
TEST_MAX_RETRIES = 3

# Test data cleanup interval in seconds
TEST_CLEANUP_INTERVAL = 3600

# ===== LAMBDA CONSTANTS =====

# Maximum OAuth token length for Lambda validation
LAMBDA_OAUTH_TOKEN_MAX_LENGTH = 2048

# Minimum OAuth token length for Lambda validation
LAMBDA_OAUTH_TOKEN_MIN_LENGTH = 100

# Default timeout for Lambda HTTP requests (seconds)
LAMBDA_DEFAULT_TIMEOUT = 30

# Maximum Lambda timeout (seconds)
LAMBDA_MAX_TIMEOUT = 300

# Minimum Lambda timeout (seconds)
LAMBDA_MIN_TIMEOUT = 1

# ===== HTTP CLIENT ADDITIONAL CONSTANTS =====

# Maximum backoff cap for HTTP retries (seconds)
HTTP_MAX_BACKOFF_CAP = 30.0

# Connection pool lifetime (seconds)
HTTP_CONNECTION_POOL_LIFETIME = 300.0

# ===== CLOUDWATCH CONSTANTS =====

# CloudWatch metric period - short term (seconds)
CLOUDWATCH_SHORT_PERIOD = 60

# CloudWatch metric period - long term (seconds)
CLOUDWATCH_LONG_PERIOD = 300


# ===== EXPORTS =====

__all__ = [
    # HTTP constants
    "HTTP_DEFAULT_TIMEOUT",
    "HTTP_LONG_TIMEOUT",
    "HTTP_MAX_RETRIES",
    "HTTP_BACKOFF_FACTOR",
    "HTTP_MAX_REDIRECTS",

    # Cache constants
    "CACHE_DEFAULT_TTL",
    "CACHE_MAX_BYTES",
    "CACHE_MAX_ENTRIES",
    "CACHE_RATE_LIMIT_WINDOW_MS",
    "CACHE_RATE_LIMIT_MAX_OPS",
    "CACHE_MEMORY_CHECK_INTERVAL_MS",
    "CACHE_MEMORY_CHECK_SAMPLE_RATE",

    # String validation constants
    "STRING_MIN_LENGTH",
    "STRING_MAX_LENGTH",
    "STRING_LOG_MAX_LENGTH",
    "STRING_CONVERSION_MAX_LENGTH",

    # Utility constants
    "UTILITY_CACHE_TTL",
    "UTILITY_UUID_VERSION",

    # Network constants
    "WEBSOCKET_CONNECT_TIMEOUT",
    "WEBSOCKET_READ_TIMEOUT",
    "WEBSOCKET_PING_INTERVAL",
    "WEBSOCKET_PING_TIMEOUT",

    # Circuit breaker constants
    "CIRCUIT_BREAKER_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_RECOVERY_TIMEOUT",
    "CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS",

    # Security constants
    "SECURITY_MAX_TOKEN_LENGTH",
    "SECURITY_MAX_URL_LENGTH",
    "SECURITY_SALT_LENGTH",
    "SECURITY_TOKEN_LENGTH",

    # Logging constants
    "LOGGING_MAX_BUFFER_SIZE",
    "LOGGING_MAX_MESSAGE_LENGTH",
    "LOGGING_DEBUG_SAMPLE_RATE",

    # Performance constants
    "PERFORMANCE_DEFAULT_SAMPLE_RATE",
    "PERFORMANCE_MAX_METRICS",
    "PERFORMANCE_PROFILING_INTERVAL_MS",

    # Metadata constants
    "METADATA_MAX_EVENT_QUEUE_SIZE",
    "METADATA_EVENT_TIMEOUT",

    # Testing constants
    "TEST_DEFAULT_TIMEOUT",
    "TEST_MAX_RETRIES",
    "TEST_CLEANUP_INTERVAL",

    # Lambda constants
    "LAMBDA_OAUTH_TOKEN_MAX_LENGTH",
    "LAMBDA_OAUTH_TOKEN_MIN_LENGTH",
    "LAMBDA_DEFAULT_TIMEOUT",
    "LAMBDA_MAX_TIMEOUT",
    "LAMBDA_MIN_TIMEOUT",

    # HTTP client additional constants
    "HTTP_MAX_BACKOFF_CAP",
    "HTTP_CONNECTION_POOL_LIFETIME",

    # CloudWatch constants
    "CLOUDWATCH_SHORT_PERIOD",
    "CLOUDWATCH_LONG_PERIOD",
]
