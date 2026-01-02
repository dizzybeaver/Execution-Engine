# EE Web Console Launcher

Web Console launcher for EE using the Unified Gateway (UG).

## Usage

### Direct Python Execution

```bash
python launcher_web.py [options]
```

### Windows Batch File

```cmd
launcher_web.bat [options]
```

## Options

- `--host HOST`: Host to bind to (default: 127.0.0.1)
- `--port PORT`: Port to bind to (default: 9000)
- `--background`: Run server in background (non-blocking)

## Examples

### Start Web Console on Default Port (9000)

```bash
python launcher_web.py
```

Output:
```
Creating Web Console on 127.0.0.1:9000
Starting Web Console on http://127.0.0.1:9000
```

### Start Web Console on Custom Port

```bash
python launcher_web.py --port 8090
```

### Start Web Console in Background

```bash
python launcher_web.py --background
```

### Start Web Console on All Interfaces

```bash
python launcher_web.py --host 0.0.0.0 --port 9000
```

## Web Console Features

Once started, the Web Console provides:

### Browser-Based Interface
- Navigate to `http://127.0.0.1:9000` in your browser
- Interactive UI for all gateway operations
- Real-time operation execution and results
- Operation history and logging

### Gateway Operations via Web
Execute any gateway operation through the web interface:

**Configuration Operations:**
- Get/Set configuration values
- List all configuration
- Reload configuration

**Security Operations:**
- Encrypt/Decrypt data
- Hash data
- Authenticate users

**Logging Operations:**
- Log messages at different levels
- Set logging level
- View logs

**Metrics Operations:**
- Increment counters
- Set gauges
- Record histograms
- Get statistics

**And all other domain operations...**

## Web Console Routes

The Web Console gateway provides:

- `web.execute`: Execute gateway operation
- `web.list_operations`: List all web operations
- `web.list_domains`: List all registered domains
- `web.start_console`: Start web console server
- `web.stop_console`: Stop web console server
- `web.get_stats`: Get web console statistics
- `web.is_running`: Check if console is running

## Architecture

```
Web Console (HTTP)
    ↓ (receive request)
Web Console Handler
    ↓ (execute via UG)
Unified Gateway (UG)
    ↓ (route to domain)
Domain Gateways
    ↓ (implement)
EE Functionality
```

## Difference Between Dashboard and Web Console

### Dashboard (Port 8080)
- Full-featured web UI
- JSON API
- More comprehensive interface
- Better for production use

### Web Console (Port 9000)
- Lightweight browser interface
- Quick operation execution
- Simpler interface
- Better for development/testing

Both use the same UG backend and provide access to all gateway operations.

## Error Handling

The launcher provides professional error handling:

- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 2**: Import error
- **Exit Code 3**: UG initialization failed
- **Exit Code 130**: Interrupted by user (Ctrl+C)

Common errors:
- **Port in use**: Specify a different port with `--port`
- **Permission denied**: May require admin privileges for ports < 1024
- **Host not available**: Check firewall and network settings

## Security Notes

### Local Development (Default)
The Web Console binds to `127.0.0.1` by default, which is secure for local development.

### External Access
To expose the Web Console externally:
```bash
python launcher_web.py --host 0.0.0.0 --port 9000
```

**WARNING**: When exposing externally, ensure you:
1. Use appropriate firewall rules
2. Implement authentication
3. Use HTTPS in production
4. Restrict access to trusted networks

## Background Mode

When using `--background`, the server runs in a separate thread:
- The launcher continues running and keeps the server alive
- Press Ctrl+C to stop both the launcher and the server
- Useful for integration with other scripts

## Development

The launcher uses ONLY UG for all operations:

- No code reimplementations
- All operations go through `gateway.execute()`
- Professional error handling via `LauncherBase`
- Path setup for Lambda compatibility

## See Also

- [../common/launcher_base.py](../common/launcher_base.py) - Base launcher class
- [../../EE/src/gateway/web/](../../EE/src/gateway/web/) - Web console implementation
- [../../EE/src/gateway/gateway.py](../../EE/src/gateway/gateway.py) - UG implementation
