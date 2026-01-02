# EE Flask Server Launcher

Flask web server launcher for EE with SocketIO support.

## Usage

### Direct Python Execution

```bash
python launcher_flask.py [options]
```

### Windows Batch File

```cmd
launcher_flask.bat [options]
```

## Options

- `--host HOST`: Host to bind to (default: 0.0.0.0)
- `--port PORT`: Port to bind to (default: 5000)
- `--debug`: Enable debug mode (auto-reload on code changes)

## Examples

### Start Flask Server on Default Port (5000)

```bash
python launcher_flask.py
```

Output:
```
UG initialized for Flask server
Starting Flask server on http://0.0.0.0:5000
```

### Start Flask Server on Custom Port

```bash
python launcher_flask.py --port 8080
```

### Start Flask Server with Debug Mode

```bash
python launcher_flask.py --debug
```

### Start Flask Server on Localhost Only

```bash
python launcher_flask.py --host 127.0.0.1 --port 5000
```

## Flask Server Features

The EE Flask server provides:

### Modern Web Interface
- Navigate to `http://0.0.0.0:5000` in your browser
- Responsive design for desktop and mobile
- Real-time updates via SocketIO

### Real-Time Communication
- WebSocket support via Flask-SocketIO
- Live updates for gateway operations
- Event-driven architecture

### Gateway Integration
- Full access to all UG operations
- Execute gateway operations from web UI
- View results in real-time

### Static Assets
- CSS, JavaScript, and images
- Modern web frameworks support
- RESTful API endpoints

## Architecture

```
Flask Server (HTTP + WebSocket)
    ↓ (request)
Flask Routes
    ↓ (execute via UG)
Unified Gateway (UG)
    ↓ (route to domain)
Domain Gateways
    ↓ (implement)
EE Functionality
```

## Flask vs Dashboard vs Web Console

### Flask Server (Port 5000)
- Modern web framework
- Real-time WebSocket support
- Full-featured web application
- Best for production web interface

### Dashboard (Port 8080)
- Built-in HTTP server
- JSON API
- Lightweight web UI
- Good for quick testing

### Web Console (Port 9000)
- Simple browser interface
- Operation execution only
- Minimal interface
- Good for development

All three interfaces use the same UG backend.

## SocketIO Events

The Flask server supports real-time SocketIO events:

### Client to Server
```javascript
// Execute gateway operation
socket.emit('execute', {
  route: 'config.get',
  payload: { key: 'test' }
});

// Listen for response
socket.on('result', (data) => {
  console.log('Result:', data);
});
```

### Server to Client
```javascript
// Listen for gateway updates
socket.on('gateway_update', (data) => {
  console.log('Update:', data);
});

// Listen for log messages
socket.on('log_message', (data) => {
  console.log('Log:', data);
});
```

## Debug Mode

Enable debug mode for development:
```bash
python launcher_flask.py --debug
```

Debug mode provides:
- Auto-reload on code changes
- Detailed error messages
- Debugger support
- Development server

## Production Deployment

For production, consider:

1. **Use production WSGI server** (e.g., Gunicorn):
   ```bash
   gunicorn -k gevent -w 4 --worker-connections 1000 module:app
   ```

2. **Use production SocketIO server** (e.g., Gunicorn with eventlet):
   ```bash
   gunicorn --worker-class socketio SGIServer -w 1 module:app
   ```

3. **Use reverse proxy** (nginx/Apache):
   - SSL termination
   - Static file serving
   - Load balancing

4. **Enable proper logging**:
   - Configure Flask logging
   - Use UG logging gateway
   - Monitor server health

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
- **Module not found**: Install Flask and SocketIO dependencies

## Dependencies

The Flask server requires:
- Flask
- Flask-SocketIO
- python-socketio
- eventlet or gevent (for WebSocket)

Install dependencies:
```bash
pip install flask flask-socketio python-socketio eventlet
```

## Security Notes

### Local Development
```bash
python launcher_flask.py --host 127.0.0.1
```

### External Access (Production)
```bash
python launcher_flask.py --host 0.0.0.0
```

**WARNING**: When exposing externally, ensure you:
1. Use HTTPS (SSL/TLS)
2. Implement authentication
3. Use CSRF protection
4. Enable rate limiting
5. Keep dependencies updated
6. Use production WSGI server

## Development

The launcher uses ONLY UG for all operations:

- No code reimplementations
- All operations go through `gateway.execute()`
- Professional error handling via `LauncherBase`
- Path setup for Lambda compatibility

## See Also

- [../common/launcher_base.py](../common/launcher_base.py) - Base launcher class
- [../../EE/src/flask_server/](../../EE/src/flask_server/) - Flask server implementation
- [../../EE/src/gateway/gateway.py](../../EE/src/gateway/gateway.py) - UG implementation
