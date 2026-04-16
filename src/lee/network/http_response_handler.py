"""network/http_response_handler.py

HTTP response parsing, validation, and handling.
"""

import json as _json
import time

from lee.gateway import execute_operation, GatewayInterface
from lee.network.http_constants import _DEBUG_MODE

# Constants
# Default chunk size for streaming response content (8KB)
# Balances memory efficiency with I/O performance
DEFAULT_CHUNK_SIZE = 8192


# Exceptions
class HTTPError(Exception):
    """HTTP request error."""

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


# Case-insensitive headers
class CaseInsensitiveDict(dict):
    """Case-insensitive dictionary for HTTP headers."""

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)

    def items(self):
        return list(super().items())


# Response object
class HttpResponse:
    """HTTP response object."""

    def __init__(self, status, reason, headers, url, raw, stream=False):
        debug_enabled = _DEBUG_MODE

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.__init__ ENTRY - status={status}, "
                    f"url={url}, stream={stream}"
                ),
                scope='HTTP_CORE'
            )

        self.status = status
        self.reason = reason
        self.headers = CaseInsensitiveDict(headers)
        self.url = url
        self._raw = raw
        self._stream = stream
        self._content = None
        if not stream:
            self._content = raw.read()
            raw.close()

        if debug_enabled:
            content_len = len(self._content) if self._content else 0
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpResponse.__init__ EXIT - content_length={content_len}",
                scope='HTTP_CORE'
            )

    @property
    def ok(self):
        """Check if response status indicates success."""
        debug_enabled = _DEBUG_MODE
        result = 200 <= self.status < 300
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpResponse.ok - status={self.status}, ok={result}",
                scope='HTTP_CORE'
            )
        return result

    @property
    def content(self):
        """Response content as bytes."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.content ENTRY - "
                    f"_content_cached={self._content is not None}"
                ),
                scope='HTTP_CORE'
            )
        if self._content is None:
            self._content = self._raw.read()
            self._raw.close()
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message=f"HttpResponse.content - read {len(self._content)} bytes",
                    scope='HTTP_CORE'
                )
        return self._content

    @property
    def text(self):
        """Response content as text."""
        # Extract charset from content-type header with proper validation
        content_type = self.headers.get("content-type", "")
        encoding = "utf-8"  # Default to UTF-8
        if "charset=" in content_type:
            charset_part = content_type.split("charset=")[-1].split(";")[0].strip()
            if charset_part:
                encoding = charset_part
        return self.content.decode(encoding, "replace")

    def json(self):
        """Parse JSON response."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=f"HttpResponse.json ENTRY - url={self.url}",
                scope='HTTP_CORE'
            )
        result = _json.loads(self.text)
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpResponse.json EXIT - parsed successfully",
                scope='HTTP_CORE'
            )
        return result

    def iter_content(self, chunk_size=DEFAULT_CHUNK_SIZE, max_size=100*1024*1024):
        """Stream response content with size limit protection.

        Args:
            chunk_size: Bytes per chunk (default: 8KB)
            max_size: Maximum response size in bytes (default: 100MB)
                      Raises MemoryError if exceeded

        Yields:
            bytes: Content chunks

        Raises:
            MemoryError: If response exceeds max_size
        """
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.iter_content ENTRY - chunk_size={chunk_size}, "
                    f"max_size={max_size}"
                ),
                scope='HTTP_CORE'
            )
        if self._content is not None:
            data = self._content
            if len(data) > max_size:
                raise MemoryError(
                    f"Response size {len(data)} exceeds maximum {max_size} bytes"
                )
            chunks_yielded = 0
            for i in range(0, len(data), chunk_size):
                yield data[i:i+chunk_size]
                chunks_yielded += 1
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message=(
                        f"HttpResponse.iter_content EXIT - "
                        f"yielded {chunks_yielded} chunks from cached content"
                    ),
                    scope='HTTP_CORE'
                )
            return

        total_read = 0
        chunks_yielded = 0
        timeout = time.time() + 30  # 30-second timeout for content streaming
        while time.time() < timeout:
            chunk = self._raw.read(chunk_size)
            if not chunk:
                break
            total_read += len(chunk)
            chunks_yielded += 1
            if total_read > max_size:
                self._raw.close()
                raise MemoryError(
                    f"Response size {total_read} exceeds maximum {max_size} bytes"
                )
            yield chunk
        else:
            self._raw.close()
            raise TimeoutError("HTTP content streaming timed out after 30 seconds")
        self._raw.close()
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.iter_content EXIT - "
                    f"streamed {chunks_yielded} chunks, {total_read} total bytes"
                ),
                scope='HTTP_CORE'
            )

    def raise_for_status(self):
        """Raise HTTPError if response status indicates error."""
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.raise_for_status ENTRY - "
                    f"status={self.status}, ok={self.ok}"
                ),
                scope='HTTP_CORE'
            )
        if not self.ok:
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, 'log',
                    message="HttpResponse.raise_for_status - raising HTTPError",
                    scope='HTTP_CORE'
                )
            raise HTTPError(f"{self.status} {self.reason}", self)

    def to_dict(self, include_content=True, max_size=100*1024*1024):
        """Convert response to dictionary format.

        Args:
            include_content: Whether to include response content (default: True)
            max_size: Maximum response size in bytes (default: 100MB)

        Returns:
            Dictionary with standardized response format:
            {
                "success": bool,
                "status_code": int,
                "reason": str,
                "headers": dict,
                "url": str,
                "data": any (optional, if include_content=True),
                "parse_error": str (optional, if parsing failed)
            }

        Raises:
            MemoryError: If response exceeds max_size
        """
        debug_enabled = _DEBUG_MODE
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message=(
                    f"HttpResponse.to_dict ENTRY - "
                    f"include_content={include_content}"
                ),
                scope='HTTP_CORE'
            )

        result = {
            "success": self.ok,
            "status_code": self.status,
            "reason": self.reason,
            "headers": dict(self.headers.items()),
            "url": self.url,
        }

        if include_content and not self._stream:
            try:
                content_type = self.headers.get("content-type", "")
                if "application/json" in content_type:
                    result["data"] = self.json()
                else:
                    result["data"] = self.text
            except (ValueError, TypeError, _json.JSONDecodeError) as e:
                result["data"] = self.content
                result["parse_error"] = str(e)
                if debug_enabled:
                    execute_operation(
                        GatewayInterface.DEBUG, 'log',
                        message=(
                            f"HttpResponse.to_dict - "
                            f"content parsing failed: {e}"
                        ),
                        scope='HTTP_CORE'
                    )

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, 'log',
                message="HttpResponse.to_dict EXIT",
                scope='HTTP_CORE'
            )

        return result


__all__ = [
    "CaseInsensitiveDict",
    "HTTPError",
    "HttpResponse",
    "DEFAULT_CHUNK_SIZE",
]
