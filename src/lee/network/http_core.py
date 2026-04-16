"""network/http_core.py

Pure-stdlib HTTP client with connection pooling, retries, redirects,
cookies, streaming, JSON, proxy support, and pluggable auth.

This is the low-level engine used by factory and HA wrapper.

DEPRECATED: This module now re-exports from the new modular structure.
Direct imports from the specific modules are preferred:
  - http_client_base: Core HTTP client functionality
  - http_connection_pool: Connection pooling
  - http_retry_handler: Retry logic with exponential backoff
  - http_response_handler: Response parsing and handling
"""

# Re-export all public APIs from the new modular structure
from lee.network.http_client_base import HttpClient
from lee.network.http_connection_pool import ConnectionError
from lee.network.http_response_handler import (
    HTTPError,
    HttpResponse,
    CaseInsensitiveDict,
)
from lee.network.http_retry_handler import Timeout

__all__ = [
    "CaseInsensitiveDict",
    "ConnectionError",
    "HTTPError",
    "HttpClient",
    "HttpResponse",
    "Timeout",
]
