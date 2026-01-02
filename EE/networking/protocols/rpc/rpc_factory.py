"""
RPC Factory - Networking Domain

RPC protocol implementations (XML-RPC and JSON-RPC).

UG-ISP Compliant:
- Factory contains actual implementation
- Receives get_logger, get_metrics, call_operation via DI
- NO imports outside networking domain (except stdlib)
- Implements XML-RPC and JSON-RPC protocols
"""

import json
import http.client
import logging
from typing import Any, Dict, Optional, Callable, List

# Try to import xmlrpc (stdlib)
try:
    import xmlrpc.client
    XMLRPC_AVAILABLE = True
except ImportError:
    XMLRPC_AVAILABLE = False


class RPCFactory:
    """RPC factory.

    Provides RPC protocol operations:
    - XML-RPC: xmlrpc_call, xmlrpc_list_methods
    - JSON-RPC: jsonrpc_call

    UG-ISP Compliance:
    - Uses only standard library
    - Implements XML-RPC and JSON-RPC 2.0
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        get_logger: Optional[Callable] = None,
        get_metrics: Optional[Callable] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize RPC factory.

        Args:
            get_logger: Logger factory function
            get_metrics: Metrics factory function
            call_operation: Callback for cross-domain operations
        """
        if get_logger:
            self.logger = get_logger("networking.protocols.rpc")
        else:
            self.logger = logging.getLogger(__name__)

        self.metrics = get_metrics
        self.call_operation = call_operation

    def xmlrpc_call(
        self,
        host: str,
        port: int,
        method: str,
        use_ssl: bool = False,
        timeout: int = 10,
        args: Optional[List] = None,
        kwargs: Optional[Dict] = None,
        **config
    ) -> Any:
        """Call XML-RPC method.

        Args:
            host: RPC server host
            port: RPC server port
            method: Method name (can use dot notation for nested calls)
            use_ssl: Use HTTPS connection
            timeout: Request timeout in seconds
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Method return value

        Raises:
            RuntimeError: If xmlrpc client not available

        Example:
            factory = RPCFactory()
            result = factory.xmlrpc_call(
                host="example.com",
                port=8000,
                method="add",
                args=[2, 3]
            )
        """
        self.logger.debug(f"XML-RPC call: {method}")

        if not XMLRPC_AVAILABLE:
            raise RuntimeError('xmlrpc.client not available')

        args = args or []
        kwargs = kwargs or {}

        url = f'{"https" if use_ssl else "http"}://{host}:{port}'

        try:
            proxy = xmlrpc.client.ServerProxy(
                url,
                allow_none=True,
                use_datetime=True,
                verbose=False
            )

            # Navigate to method using dot notation
            obj = proxy
            for part in method.split('.'):
                obj = getattr(obj, part)

            # Call method
            result = obj(*args, **kwargs)
            return result

        except Exception as e:
            raise ConnectionError(f'XML-RPC call failed: {e}')

    def xmlrpc_list_methods(
        self,
        host: str,
        port: int,
        use_ssl: bool = False,
        timeout: int = 10,
        **kwargs
    ) -> List[str]:
        """List available XML-RPC methods.

        Args:
            host: RPC server host
            port: RPC server port
            use_ssl: Use HTTPS connection
            timeout: Request timeout in seconds

        Returns:
            List of method names

        Raises:
            RuntimeError: If xmlrpc client not available

        Example:
            factory = RPCFactory()
            methods = factory.xmlrpc_list_methods(host="example.com", port=8000)
            print(methods)
        """
        return self.xmlrpc_call(
            host=host,
            port=port,
            method='system.listMethods',
            use_ssl=use_ssl,
            timeout=timeout
        )

    def jsonrpc_call(
        self,
        host: str,
        port: int,
        method: str,
        use_ssl: bool = False,
        timeout: int = 10,
        path: str = '/',
        args: Optional[List] = None,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """Call JSON-RPC method.

        Args:
            host: RPC server host
            port: RPC server port
            method: Method name
            use_ssl: Use HTTPS connection
            timeout: Request timeout in seconds
            path: RPC endpoint path (default: '/')
            args: Positional arguments
            params: Named parameters (for params-style call)

        Returns:
            Method return value

        Example:
            factory = RPCFactory()
            result = factory.jsonrpc_call(
                host="example.com",
                port=8000,
                method="add",
                args=[2, 3]
            )
        """
        self.logger.debug(f"JSON-RPC call: {method}")

        args = args or []

        # Build params (positional or named)
        if params:
            request_params = params
        else:
            request_params = args if args else []

        # Build payload
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': request_params,
            'id': 1
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            # Create connection
            if use_ssl:
                conn = http.client.HTTPSConnection(host, port, timeout=timeout)
            else:
                conn = http.client.HTTPConnection(host, port, timeout=timeout)

            # Send request
            conn.request('POST', path, json.dumps(payload), headers)

            # Get response
            response = conn.getresponse()
            conn.close()

            if response.status != 200:
                raise ConnectionError(f'JSON-RPC request failed: HTTP {response.status}')

            # Parse response
            result = json.loads(response.read().decode('utf-8'))

            if 'error' in result:
                error = result['error']
                raise ConnectionError(f'JSON-RPC error: {error}')

            return result.get('result')

        except Exception as e:
            raise ConnectionError(f'JSON-RPC request failed: {e}')


__all__ = [
    "RPCFactory",
]
