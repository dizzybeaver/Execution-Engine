"""network/http_client_base.py

Core HTTP client functionality with request execution and high-level methods.
"""

import json as _json
import ssl
import urllib.parse
from collections.abc import Callable
from http.cookiejar import CookieJar
from typing import Any, Optional

from lee.gateway import execute_operation, GatewayInterface
from lee.lee_config.constants import (
    HTTP_DEFAULT_TIMEOUT,
    HTTP_MAX_REDIRECTS,
)
from lee.network.http_auth import _validate_header_name, _validate_header_value
from lee.network.http_constants import (
    _DEBUG_MODE,
    _PRODUCTION_MODE,
)
from lee.network.http_connection_pool import _ConnectionPool, ConnectionError
from lee.network.http_response_handler import (
    CaseInsensitiveDict,
    HttpResponse,
)
from lee.network.http_retry_handler import RetryHandler, Timeout


# HTTP Client
class HttpClient:
    """HTTP client with connection pooling, retries, and redirects."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        max_redirects: Optional[int] = None,
        default_headers: Optional[dict[str, str]] = None,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        auth_header_factory: Optional[Callable[[], dict[str, str]]] = None,
    ):
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.__init__ ENTRY - timeout={timeout}, max_retries={max_retries}",
                scope='HTTP_CLIENT'
            )

        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = (
            timeout if timeout is not None else HTTP_DEFAULT_TIMEOUT
        )
        self.max_redirects = (
            max_redirects if max_redirects is not None else HTTP_MAX_REDIRECTS
        )
        self.default_headers = CaseInsensitiveDict(default_headers or {})
        self.auth_header_factory = auth_header_factory
        self.proxy = urllib.parse.urlparse(proxy) if proxy else None

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.__init__ - configured timeout={self.timeout}s",
                scope='HTTP_CLIENT'
            )

        ctx = ssl.create_default_context()
        debug_enabled = _DEBUG_MODE

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message="HttpClient - ctx = ssl.create_default_context",
                             scope='HTTP_CLIENT')

        if not verify_ssl:
            # Security: Only allow SSL verification bypass in non-production environments
            is_production = _PRODUCTION_MODE
            if is_production:
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message='SSL verification bypass rejected - production environment',
                        scope='HTTP_CLIENT'
                    )
                raise ValueError("SSL verification cannot be disabled in production environment")
            # Log warning when SSL verification is disabled
            import sys
            print("WARNING: SSL verification is disabled - Man-in-the-middle attacks possible", file=sys.stderr)
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG,
                    'log',
                    message='SSL verification disabled - development mode',
                    scope='HTTP_CLIENT'
                )
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        self.pool = _ConnectionPool(ctx)
        debug_enabled = _DEBUG_MODE

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message="HttpClient - self.pool",
                             scope='HTTP_CLIENT')

        self.cookies = CookieJar()
        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message="HttpClient - self.cookies",
                             scope='HTTP_CLIENT')

        # Initialize retry handler
        self._retry_handler = RetryHandler(max_retries, backoff_factor)

        # Statistics tracking
        self._stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "requests_timed_out": 0,
            "retries_total": 0,
            "redirects_total": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
        }

    # Public HTTP verbs
    def get(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.get ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("GET", url, **kw)

    def post(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.post ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("POST", url, **kw)

    def put(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.put ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("PUT", url, **kw)

    def patch(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.patch ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("PATCH", url, **kw)

    def delete(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.delete ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("DELETE", url, **kw)

    def head(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.head ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("HEAD", url, **kw)

    def options(self, url, **kw):  # pylint: disable=multiple-statements
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.options ENTRY - url={url}",
                scope='HTTP_CORE'
            )
        return self.request("OPTIONS", url, **kw)

    # Core request
    def request(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        data: str | bytes | Optional[dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        stream: bool = False,
        timeout: Optional[float] = None,
        allow_redirects: bool = True,
    ) -> HttpResponse:
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpClient.request ENTRY - method={method}, url={url}, "
                    f"stream={stream}, allow_redirects={allow_redirects}"
                ),
                scope='HTTP_CORE'
            )
        full_url = self._build_url(url)
        parsed = urllib.parse.urlsplit(full_url)
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.request - full_url={full_url}",
                scope='HTTP_CORE'
            )

        # Merge query params
        if params:
            q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            q.extend((k, str(v)) for k, v in params.items())
            parsed = parsed._replace(query=urllib.parse.urlencode(q))
            full_url = urllib.parse.urlunsplit(parsed)

        # Build headers
        hdrs = self.default_headers.copy()
        if headers:
            for k, v in headers.items():
                hdrs[k] = v

        # Auth headers
        if self.auth_header_factory:
            for k, v in self.auth_header_factory().items():
                hdrs[k] = v

        # Validate all headers for CRLF injection (security fix)
        validated_headers = CaseInsensitiveDict()
        for key, value in hdrs.items():
            validated_key = _validate_header_name(key)
            validated_value = _validate_header_value(value)
            validated_headers[validated_key] = validated_value
        hdrs = validated_headers

        # Body
        body = None
        if json is not None:
            body = _json.dumps(json).encode("utf-8")
            hdrs.setdefault("content-type", "application/json")
        elif isinstance(data, dict):
            body = urllib.parse.urlencode(data).encode("utf-8")
            hdrs.setdefault("content-type", "application/x-www-form-urlencoded")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        elif isinstance(data, bytes):
            body = data

        # Retry loop
        attempt = 0
        while True:
            attempt += 1

            # Track total requests
            self._stats["requests_total"] += 1

            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message=f"HttpClient.request - attempt {attempt}/{self._retry_handler.max_retries + 1}",
                    scope='HTTP_CORE'
                )

            try:
                resp = self._send(method, parsed, full_url, hdrs, body, stream, timeout)

                # Track successful request
                self._stats["requests_successful"] += 1

                # Track bytes sent/received
                if body:
                    self._stats["bytes_sent"] += len(body)
                # pylint: disable=protected-access
                if resp._content:
                    self._stats["bytes_received"] += len(resp._content)

                if allow_redirects:
                    original_redirects = self._stats["redirects_total"]
                    resp = self._handle_redirects(method, resp, stream, timeout)
                    # Track how many redirects occurred
                    self._stats["redirects_total"] += (
                        self._stats["redirects_total"] - original_redirects
                    )

                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=(
                            f"HttpClient.request EXIT - success={resp.ok}, "
                            f"status={resp.status}"
                        ),
                        scope='HTTP_CORE'
                    )

                return resp

            except TimeoutError as exc:
                self._stats["requests_timed_out"] += 1
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=f"HttpClient.request - TimeoutError on attempt {attempt}",
                        scope='HTTP_CORE'
                    )
                if not self._retry_handler.should_retry(attempt, TimeoutError):
                    self._stats["requests_failed"] += 1
                    raise Timeout("Request timed out") from exc
                self._stats["retries_total"] += 1
                self._retry_handler.wait_with_backoff(attempt)

            except OSError as exc:
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=f"HttpClient.request - OSError on attempt {attempt}: {exc}",
                        scope='HTTP_CORE'
                    )
                if not self._retry_handler.should_retry(attempt, OSError):
                    self._stats["requests_failed"] += 1
                    raise ConnectionError("Connection failed") from exc
                self._stats["retries_total"] += 1
                self._retry_handler.wait_with_backoff(attempt)

    # Low-level send
    def _send(self, method, parsed, url, headers, body, stream, timeout):  # pylint: disable=too-many-arguments,too-many-locals
        debug_enabled = _DEBUG_MODE

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"HttpClient._send ENTRY - method={method}, url={url}, timeout={timeout or self.timeout}",
                             scope='HTTP_CORE')

        scheme = parsed.scheme
        host = parsed.hostname
        port = parsed.port or (443 if scheme == "https" else 80)

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"About to call pool.get(scheme={scheme}, host={host}, port={port}, timeout={timeout or self.timeout})",
                             scope='HTTP_CORE')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='before_pool_get',
                             scope='HTTP_CORE')

        conn = self.pool.get(scheme, host, port, self.proxy, timeout=timeout or self.timeout)

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='after_pool_get',
                             scope='HTTP_CORE')
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"pool.get returned - conn={type(conn).__name__}",
                             scope='HTTP_CORE')

        # Proxy target
        if self.proxy:
            target = url
        else:
            target = parsed.path or "/"
            if parsed.query:
                target += "?" + parsed.query

        # Host header
        headers.setdefault("host", f"{host}:{port}")

        # Send
        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"About to call conn.request(method={method}, target={target})",
                             scope='HTTP_CORE')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='before_conn_request',
                             scope='HTTP_CORE')

        try:
            conn.request(method, target, body=body, headers=dict(headers.items()))

            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'timing',
                                 operation_name='after_conn_request',
                                 scope='HTTP_CORE')
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message="conn.request complete, about to call conn.getresponse()",
                                 scope='HTTP_CORE')
                execute_operation(GatewayInterface.DEBUG, 'timing',
                                 operation_name='before_conn_getresponse',
                                 scope='HTTP_CORE')

            raw = conn.getresponse()

            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'timing',
                                 operation_name='after_conn_getresponse',
                                 scope='HTTP_CORE')
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"conn.getresponse returned - status={raw.status}",
                                scope='HTTP_CORE')
                execute_operation(GatewayInterface.DEBUG, 'timing',
                                 operation_name='http_send_complete',
                                 scope='HTTP_CORE')

        except (ConnectionError, TimeoutError, OSError):
            # Remove broken connection from pool
            self.pool.mark_broken(scheme, host, port, self.proxy)
            try:
                conn.close()
            except (OSError, ConnectionError) as e:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        'log_error',
                        message=f'(IOError, OSError, ConnectionError) occurred: {e}',
                        corr_id=None
                    )
                except (ImportError, AttributeError, RuntimeError):
                    pass  # Gateway not available
            raise

        resp_headers = {k.lower(): v for k, v in raw.getheaders()}
        return HttpResponse(raw.status, raw.reason, resp_headers, url, raw, stream)

    # Redirects
    def _handle_redirects(self, method, resp, stream, timeout):
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpClient._handle_redirects ENTRY - status={resp.status}, "
                    f"max_redirects={self.max_redirects}"
                ),
                scope='HTTP_CORE'
            )
        redirects = self.max_redirects
        while resp.status in (301, 302, 303, 307, 308) and redirects > 0:
            loc = resp.headers.get("location")
            if not loc:
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=(
                            "HttpClient._handle_redirects - "
                            "no location header, stopping redirect"
                        ),
                        scope='HTTP_CORE'
                    )
                break
            new_url = urllib.parse.urljoin(resp.url, loc)
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message=(
                        f"HttpClient._handle_redirects - redirecting to: {new_url}, "
                        f"redirects_remaining={redirects - 1}"
                    ),
                    scope='HTTP_CORE'
                )

            # Security: Validate redirect URL to prevent SSRF attacks
            try:
                from lee.network.ssrf_protect import validate_url
                validate_url(new_url)
            except ValueError as e:
                # Block redirect to unsafe URL (SSRF protection)
                # Log the blocked redirect attempt for security monitoring
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(  # pylint: disable=logging-fstring-interpolation
                    "Blocked redirect to unsafe URL (SSRF protection): %s. Reason: %s",
                    new_url, e
                )
                # Return the redirect response without following it
                # This prevents following malicious redirects to internal resources
                break

            resp = self.request(method, new_url, stream=stream, timeout=timeout)
            redirects -= 1
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpClient._handle_redirects EXIT - final_status={resp.status}, "
                    f"redirects_used={self.max_redirects - redirects}"
                ),
                scope='HTTP_CORE'
            )
        return resp

    # Helpers
    def _build_url(self, url):
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpClient._build_url ENTRY - url={url}, "
                    f"base_url={self.base_url}"
                ),
                scope='HTTP_CORE'
            )
        if self.base_url and not urllib.parse.urlsplit(url).scheme:
            result = urllib.parse.urljoin(self.base_url + "/", url.lstrip("/"))
        else:
            result = url
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient._build_url EXIT - result={result}",
                scope='HTTP_CORE'
            )
        return result

    def get_statistics(self) -> dict[str, Any]:
        """Get HTTP client statistics including connection pool metrics.

        Returns:
            Dictionary containing request statistics and pool metrics

        """
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpClient.get_statistics ENTRY",
                scope='HTTP_CORE'
            )
        stats = self._stats.copy()
        stats["connection_pool"] = self.pool.get_pool_stats()
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpClient.get_statistics EXIT - {stats}",
                scope='HTTP_CORE'
            )
        return stats.copy()

    def reset_statistics(self) -> None:
        """Reset HTTP client statistics."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpClient.reset_statistics ENTRY",
                scope='HTTP_CORE'
            )
        self._stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "requests_timed_out": 0,
            "retries_total": 0,
            "redirects_total": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
        }
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpClient.reset_statistics EXIT - statistics reset",
                scope='HTTP_CORE'
            )

    def configure_retry(
        self,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """Configure retry policy.

        Args:
            max_retries: Maximum number of retry attempts (None to keep current)
            backoff_factor: Backoff multiplier for retries (None to keep current)
        """
        self._retry_handler.configure_retry(max_retries, backoff_factor)

    def close(self):
        """Close all connections in the pool."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpClient.close ENTRY - closing all connections",
                scope='HTTP_CORE'
            )
        self.pool.close_all()
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpClient.close EXIT - all connections closed",
                scope='HTTP_CORE'
            )


__all__ = [
    "_DEBUG_MODE",
    "_PRODUCTION_MODE",
    "HttpClient",
]
