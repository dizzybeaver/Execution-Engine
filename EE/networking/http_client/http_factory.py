"""
HTTP Factory - Networking Domain

HTTP client implementation using urllib (stdlib) with optional requests library.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation factory functions via DI
- NO imports outside networking domain (except stdlib)
- Optional requests library with graceful fallback
"""

import logging
import json
from typing import Any, Dict, Optional, Callable, Union

# Import urllib modules with aliases to avoid naming conflicts
import urllib.request as urllib_request
import urllib.error as urllib_error
import urllib.parse as urllib_parse


class HTTPFactory:
    """HTTP factory.

    Provides HTTP client operations:
    - GET, POST, PUT, DELETE requests
    - Custom request method
    - Header management
    - Response parsing

    UG-ISP Compliance:
    - Uses urllib from standard library
    - Optional requests library with graceful fallback
    - Cross-domain calls via call_operation callback
    """

    # MODIFIED: EE 2.1 compliant constructor - receives factory functions
    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize HTTP factory.

        Args:
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            call_operation: Callback for cross-domain operations with signature: call_operation(domain, interface, operation, **kwargs)
        """
        # Create logger using factory function
        if get_logger:
            self.logger = get_logger("networking.http")
        else:
            self.logger = logging.getLogger(__name__)

        self.get_metrics = get_metrics
        self.call_operation = call_operation

        # Try to import requests library (optional)
        self.requests = None
        try:
            import requests as requests_lib
            self.requests = requests_lib
            self.logger.debug("Using requests library for HTTP operations")
        except ImportError:
            self.logger.debug("requests library not available, using urllib")

    def _build_response(self, status: int, headers: Dict[str, str], body: Any) -> Dict[str, Any]:
        """Build standardized response dictionary.

        Args:
            status: HTTP status code
            headers: Response headers
            body: Response body

        Returns:
            Standardized response dict
        """
        return {
            "status": status,
            "headers": headers,
            "body": body,
        }

    def _parse_headers(self, raw_headers: str) -> Dict[str, str]:
        """Parse raw headers string to dict.

        Args:
            raw_headers: Raw headers string

        Returns:
            Headers dictionary
        """
        headers = {}
        for line in raw_headers.split('\r\n')[1:]:  # Skip status line
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers

    def _request_urllib(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[str, bytes, Dict]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make HTTP request using urllib.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request body
            params: URL parameters
            timeout: Request timeout in seconds

        Returns:
            Response dictionary
        """
        # Build URL with params
        if params:
            query_string = urllib_parse.urlencode(params)
            url = f"{url}?{query_string}" if '?' not in url else f"{url}&{query_string}"

        # Prepare request
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
            headers = headers or {}
            headers['Content-Type'] = 'application/json'

        req = urllib_request.Request(
            url,
            data=data,
            headers=headers or {},
            method=method.upper()
        )

        try:
            with urllib_request.urlopen(req, timeout=timeout) as response:
                body = response.read()

                # Try to parse as JSON
                try:
                    body = json.loads(body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Return as string or bytes
                    try:
                        body = body.decode('utf-8')
                    except UnicodeDecodeError:
                        body = body

                return self._build_response(
                    status=response.status,
                    headers=self._parse_headers(str(response.headers)),
                    body=body
                )

        except urllib_error.HTTPError as e:
            return self._build_response(
                status=e.code,
                headers=self._parse_headers(str(e.headers)) if e.headers else {},
                body={"error": str(e)}
            )
        except urllib_error.URLError as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def _request_requests(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[str, bytes, Dict]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request using requests library.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            data: Request body
            params: URL parameters
            timeout: Request timeout in seconds
            json_data: JSON data to send

        Returns:
            Response dictionary
        """
        try:
            response = self.requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                params=params,
                timeout=timeout
            )

            # Try to parse JSON response
            try:
                body = response.json()
            except ValueError:
                body = response.text

            return self._build_response(
                status=response.status_code,
                headers=dict(response.headers),
                body=body
            )

        except self.requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP GET request.

        Args:
            url: Request URL
            headers: Request headers
            params: URL parameters
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with status, headers, body

        Example:
            factory = HTTPFactory()
            response = factory.get(
                url="https://api.example.com/users",
                params={"page": 1},
                headers={"Accept": "application/json"}
            )
        """
        self.logger.debug(f"HTTP GET: {url}")

        if self.requests:
            return self._request_requests("GET", url, headers=headers, params=params, timeout=timeout)
        else:
            return self._request_urllib("GET", url, headers=headers, params=params, timeout=timeout)

    def post(
        self,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP POST request.

        Args:
            url: Request URL
            data: Request body (string, bytes, or dict)
            json_data: JSON data to send
            headers: Request headers
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with status, headers, body

        Example:
            factory = HTTPFactory()
            response = factory.post(
                url="https://api.example.com/users",
                json_data={"name": "John", "email": "john@example.com"}
            )
        """
        self.logger.debug(f"HTTP POST: {url}")

        if self.requests:
            return self._request_requests("POST", url, headers=headers, data=data, json_data=json_data, timeout=timeout)
        else:
            # For urllib, json_data is passed as data
            if json_data:
                data = json_data
            return self._request_urllib("POST", url, headers=headers, data=data, timeout=timeout)

    def put(
        self,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP PUT request.

        Args:
            url: Request URL
            data: Request body
            json_data: JSON data to send
            headers: Request headers
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with status, headers, body

        Example:
            factory = HTTPFactory()
            response = factory.put(
                url="https://api.example.com/users/1",
                json_data={"name": "John Updated"}
            )
        """
        self.logger.debug(f"HTTP PUT: {url}")

        if self.requests:
            return self._request_requests("PUT", url, headers=headers, data=data, json_data=json_data, timeout=timeout)
        else:
            if json_data:
                data = json_data
            return self._request_urllib("PUT", url, headers=headers, data=data, timeout=timeout)

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP DELETE request.

        Args:
            url: Request URL
            headers: Request headers
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with status, headers, body

        Example:
            factory = HTTPFactory()
            response = factory.delete(
                url="https://api.example.com/users/1"
            )
        """
        self.logger.debug(f"HTTP DELETE: {url}")

        if self.requests:
            return self._request_requests("DELETE", url, headers=headers, timeout=timeout)
        else:
            return self._request_urllib("DELETE", url, headers=headers, timeout=timeout)

    def request(
        self,
        method: str,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """Custom HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            url: Request URL
            data: Request body
            json_data: JSON data to send
            headers: Request headers
            params: URL parameters
            timeout: Request timeout in seconds

        Returns:
            Response dictionary with status, headers, body

        Example:
            factory = HTTPFactory()
            response = factory.request(
                method="PATCH",
                url="https://api.example.com/users/1",
                json_data={"email": "newemail@example.com"}
            )
        """
        self.logger.debug(f"HTTP {method}: {url}")

        if self.requests:
            return self._request_requests(method, url, headers=headers, data=data, json_data=json_data, params=params, timeout=timeout)
        else:
            if json_data:
                data = json_data
            return self._request_urllib(method, url, headers=headers, data=data, params=params, timeout=timeout)


__all__ = [
    "HTTPFactory",
]
