"""
http_client/__init__.py
Version: 2025-12-10_1
Purpose: HTTP client module exports
License: Apache 2.0
"""

# Core manager
from http_client.http_client_manager import (
    HTTPClientCore,
    get_http_client_manager,
    get_http_client,
)

# Operations (internal use)
from http_client.http_client_operations import (
    http_request_implementation,
    http_get_implementation,
    http_post_implementation,
    http_put_implementation,
    http_delete_implementation,
    http_reset_implementation,
    get_state_implementation,
    reset_state_implementation,
)

# State management
from http_client.http_client_state import (
    get_client_state,
    reset_client_state,
    configure_http_retry,
    get_connection_statistics,
)

# Utilities
from http_client.http_client_utilities import (
    get_standard_headers,
    get_ha_headers,
    build_query_string,
    parse_response_headers,
    process_response,
)

# Transformation
from http_client.http_client_transformation import (
    ResponseTransformer,
    TransformationPipeline,
    transform_http_response,
    create_transformer,
    create_pipeline,
)

# Validation
from http_client.http_client_validation import (
    HTTPMethod,
    ResponseValidator,
    validate_http_response,
    create_validator,
)

__all__ = [
    # Core manager
    'HTTPClientCore',
    'get_http_client_manager',
    'get_http_client',
    
    # Operations (internal)
    'http_request_implementation',
    'http_get_implementation',
    'http_post_implementation',
    'http_put_implementation',
    'http_delete_implementation',
    'http_reset_implementation',
    'get_state_implementation',
    'reset_state_implementation',
    
    # State
    'get_client_state',
    'reset_client_state',
    'configure_http_retry',
    'get_connection_statistics',
    
    # Utilities
    'get_standard_headers',
    'get_ha_headers',
    'build_query_string',
    'parse_response_headers',
    'process_response',
    
    # Transformation
    'ResponseTransformer',
    'TransformationPipeline',
    'transform_http_response',
    'create_transformer',
    'create_pipeline',
    
    # Validation
    'HTTPMethod',
    'ResponseValidator',
    'validate_http_response',
    'create_validator',
]
