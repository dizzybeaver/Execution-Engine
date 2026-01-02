# EE Dashboard Launcher

Dashboard server launcher for EE using the Unified Gateway (UG).

## Usage

### Direct Python Execution

```bash
python launcher_dashboard.py [options]
```

### Windows Batch File

```cmd
launcher_dashboard.bat [options]
```

## Options

- `--host HOST`: Host to bind to (default: 127.0.0.1)
- `--port PORT`: Port to bind to (default: 8080)
- `--auto-port`: Automatically find available port if default is in use

## Examples

### Start Dashboard on Default Port (8080)

```bash
python launcher_dashboard.py
```

Output:
```
Creating Dashboard server on 127.0.0.1:8080
Starting Dashboard server on http://127.0.0.1:8080
```

### Start Dashboard on Custom Port

```bash
python launcher_dashboard.py --port 9090
```

### Start Dashboard on All Interfaces

```bash
python launcher_dashboard.py --host 0.0.0.0 --port 8080
```

### Auto-Find Available Port

```bash
python launcher_dashboard.py --auto-port
```

## Dashboard Features

Once started, the Dashboard provides:

### Web Interface
- Navigate to `http://127.0.0.1:8080` in your browser
- Interactive UI for all gateway operations
- Real-time operation execution and results

### JSON API
Execute operations via HTTP POST:

```bash
# Execute gateway operation
curl -X POST http://127.0.0.1:8080/api/execute \
  -H "Content-Type: application/json" \
  -d '{"route": "config.get", "payload": {"key": "test"}}'

# List all domains
curl http://127.0.0.1:8080/api/domains

# Get gateway statistics
curl http://127.0.0.1:8080/api/stats
```

## API Endpoints

### GET /api/domains
List all registered domain gateways.

Response:
```json
{
  "domains": ["config", "security", "logging", "metrics", ...],
  "count": 10
}
```

### GET /api/operations/{domain}
List all operations in a domain.

```bash
curl http://127.0.0.1:8080/api/operations/config
```

Response:
```json
{
  "domain": "config",
  "operations": [
    {
      "route": "config.get",
      "description": "Get configuration value",
      "params": {"key": "str", "default": "any (optional)"}
    },
    ...
  ]
}
```

### POST /api/execute
Execute a gateway operation.

Request:
```json
{
  "route": "config.get",
  "payload": {
    "key": "database.host"
  }
}
```

Response:
```json
{
  "success": true,
  "result": "localhost"
}
```

### GET /api/stats
Get gateway statistics.

Response:
```json
{
  "total_routes": 50,
  "total_domains": 10,
  "route_stats": {
    "config.get": {"calls": 100, "errors": 0, "avg_time_ms": 0.5}
  }
}
```

## Architecture

```
Dashboard Server (HTTP)
    ↓ (receive request)
Dashboard Handler
    ↓ (execute via UG)
Unified Gateway (UG)
    ↓ (route to domain)
Domain Gateways
    ↓ (implement)
EE Functionality
```

## Error Handling

The launcher provides professional error handling:

- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 2**: Import error
- **Exit Code 3**: UG initialization failed
- **Exit Code 130**: Interrupted by user (Ctrl+C)

Common Dashboard errors:
- **Port in use**: Use `--auto-port` or specify a different port
- **Permission denied**: May require admin privileges for ports < 1024
- **Host not available**: Check firewall and network settings

## Security Notes

### Local Development (Default)
The Dashboard binds to `127.0.0.1` by default, which is secure for local development.

### External Access
To expose the Dashboard externally:
```bash
python launcher_dashboard.py --host 0.0.0.0 --port 8080
```

**WARNING**: When exposing externally, ensure you:
1. Use appropriate firewall rules
2. Implement authentication
3. Use HTTPS in production
4. Restrict access to trusted networks

## Development

The launcher uses ONLY UG for all operations:

- No code reimplementations
- All operations go through `gateway.execute()`
- Professional error handling via `LauncherBase`
- Path setup for Lambda compatibility

## See Also

- [../common/launcher_base.py](../common/launcher_base.py) - Base launcher class
- [../../EE/src/gateway/dashboard/](../../EE/src/gateway/dashboard/) - Dashboard implementation
- [../../EE/src/gateway/gateway.py](../../EE/src/gateway/gateway.py) - UG implementation
