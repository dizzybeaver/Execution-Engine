# EE Dashboard Domain Gateway

The Dashboard Domain Gateway provides a web-based interface for interacting with the EE Universal Gateway. It serves both an interactive web UI and JSON API endpoints.

## Architecture

```
Universal Gateway -> Domain Registry -> Dashboard Domain -> HTTP Server
```

## Components

### 1. dashboard/__init__.py
Main module exports for the Dashboard domain.

### 2. dashboard_common.py
Error classes and common utilities:
- `DashboardError`: Base error for all Dashboard failures
- `DashboardServerError`: Server lifecycle errors
- `DashboardRequestError`: HTTP request handling errors

### 3. dashboard_handler.py
HTTP request handler with GET/POST support:
- Serves interactive web UI at `/`
- JSON API endpoints for gateway operations
- Integrated with EE gateway registry

### 4. dashboard_server_factory.py
Factory functions for creating Dashboard servers:
- `create_dashboard_server()`: Create server on specified port
- `create_dashboard_server_with_auto_port()`: Auto-select available port
- `find_available_port()`: Utility for port discovery

## Usage

### Basic Example

```python
from gateway.gateway_registry import EEDomainRegistry
from gateway.dashboard import create_dashboard_server

# Get registry
registry = EEDomainRegistry.get_instance()

# Create and start dashboard server
server = create_dashboard_server(registry, port=8080)
server.serve_forever()
```

### Auto Port Selection

```python
server = create_dashboard_server_with_auto_port(
    registry,
    host="127.0.0.1",
    starting_port=8080,
    max_attempts=10
)
print(f"Server running on port {server.port}")
server.serve_forever()
```

## HTTP Endpoints

### GET Endpoints

- `GET /` - Serve interactive web UI
- `GET /index.html` - Serve web UI
- `GET /health` - Health check
- `GET /list-domains` - List all registered domains
- `GET /list-routes` - List all routes for all domains

### POST Endpoints

- `POST /exec/{route}` - Execute a gateway route

  Example:
  ```bash
  curl -X POST http://localhost:8080/exec/test.add \
    -H "Content-Type: application/json" \
    -d '{"a": 5, "b": 3}'
  ```

  Response:
  ```json
  {
    "data": {
      "result": 8
    }
  }
  ```

## Integration with Gateway Registry

The Dashboard integrates seamlessly with the EE gateway registry:

```python
from gateway.gateway_registry import EEDomainRegistry
from gateway.dashboard import create_dashboard_server

registry = EEDomainRegistry.get_instance()

# Domains automatically available through dashboard
domains = registry.list_domains()
# ['config', 'security', 'logging', 'metrics', 'debug',
#  'serialization', 'isp', 'cli', 'dashboard']

server = create_dashboard_server(registry, port=8080)
```

## Web UI Features

The interactive web UI provides:

1. **Domain Navigation**: Sidebar with all registered domains
2. **Route Browser**: View available routes for each domain
3. **Payload Editor**: JSON editor for request payloads
4. **Execution**: Execute routes and view results
5. **Real-time Updates**: Live interaction with gateway

## Testing

Run the integration test:

```bash
python src/gateway/dashboard/test_dashboard_integration.py
```

This will:
1. Create a test domain gateway
2. Register it with the gateway registry
3. Start the dashboard server
4. Test all HTTP endpoints
5. Verify integration

## Security Notes

1. **Default Binding**: Server binds to `127.0.0.1` by default (localhost only)
2. **External Access**: Use `host="0.0.0.0"` to expose externally
3. **Authentication**: Add authentication layer for production use
4. **HTTPS**: Configure SSL/TLS for secure connections

## Error Handling

All Dashboard errors extend `DashboardError`:

```python
from gateway.dashboard import DashboardError, DashboardServerError

try:
    server = create_dashboard_server(registry, port=8080)
    server.serve_forever()
except DashboardServerError as e:
    print(f"Server error: {e.error_code} - {e}")
    print(f"Context: {e.context}")
```

## Reference Implementation

Based on the Universal Gateway pattern from:
`D:\Code\Project\Gateway\dashboard\`

## Files Created

```
D:\Code\Project\EE\src\gateway\dashboard\
├── __init__.py                      # Module exports
├── dashboard_common.py              # Error classes
├── dashboard_handler.py             # HTTP handler
├── dashboard_server_factory.py      # Server factory
├── test_dashboard_integration.py    # Integration tests
└── README.md                        # This file
```

## Integration Status

- [x] Module structure created
- [x] Error classes implemented
- [x] HTTP handler implemented
- [x] Server factory implemented
- [x] Integration tests passing
- [x] Gateway registry integration verified
- [x] Web UI template included
- [x] JSON API endpoints functional
