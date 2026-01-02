# EE Launcher System

Complete launcher system for EE (Enterprise Environment) using the Unified Gateway (UG).

## Overview

The EE launcher system provides multiple interfaces for interacting with all EE gateway operations. All launchers:

- Use ONLY the Unified Gateway (UG) for all operations
- Include proper path setup for Lambda compatibility
- Provide professional error handling
- Support all gateway domains (config, security, logging, metrics, etc.)

## Architecture

```
menu.bat (Main Menu)
    ├── launcher_cli.py (CLI Interface)
    ├── launcher_dashboard.py (Dashboard Server)
    ├── launcher_web.py (Web Console)
    └── launcher_flask.py (Flask Server)
            ↓
    launcher_base.py (Common Base)
            ↓
    Unified Gateway (UG)
            ↓
    Domain Gateways
            ↓
    EE Functionality
```

## Quick Start

### Using Main Menu (Recommended)

Double-click `menu.bat` in the project root to launch the main menu:

```cmd
D:\Code\Project\menu.bat
```

This will present a menu with all available interfaces.

### Direct Launcher Execution

You can also run individual launchers directly:

#### CLI Launcher
```cmd
launcher\cli\launcher_cli.bat list-domains
launcher\cli\launcher_cli.bat exec config.get --payload "{\"key\": \"test\"}"
```

#### Dashboard Launcher
```cmd
launcher\dashboard\launcher_dashboard.bat
launcher\dashboard\launcher_dashboard.bat --port 8080
```

#### Web Console Launcher
```cmd
launcher\web\launcher_web.bat
launcher\web\launcher_web.bat --port 9000
```

#### Flask Launcher
```cmd
launcher\flask\launcher_flask.bat
launcher\flask\launcher_flask.bat --port 5000 --debug
```

## Interfaces

### 1. Command-Line Interface (CLI)

**Launcher:** `launcher/cli/launcher_cli.py`

**Features:**
- Interactive terminal interface
- Execute gateway operations via commands
- List domains, operations, and execute routes
- JSON output format support

**Common Commands:**
```bash
# List all domains
launcher_cli.bat list-domains

# Execute operation
launcher_cli.bat exec config.get --payload "{\"key\": \"test\"}"

# JSON output
launcher_cli.bat --json exec security.encrypt --payload "{\"data\": \"secret\"}"

# Gateway statistics
launcher_cli.bat stats
```

**Documentation:** [launcher/cli/README.md](launcher/cli/README.md)

---

### 2. Dashboard Server

**Launcher:** `launcher/dashboard/launcher_dashboard.py`

**Port:** 8080 (default)

**Features:**
- Full-featured web UI
- JSON API for programmatic access
- Operation history and logging
- Best for production use

**API Endpoints:**
- `GET /api/domains` - List all domains
- `GET /api/operations/{domain}` - List domain operations
- `POST /api/execute` - Execute operation
- `GET /api/stats` - Gateway statistics

**Example:**
```bash
# Start dashboard
launcher_dashboard.bat --port 8080

# Access in browser
http://127.0.0.1:8080

# API call
curl -X POST http://127.0.0.1:8080/api/execute \
  -H "Content-Type: application/json" \
  -d "{\"route\": \"config.get\", \"payload\": {\"key\": \"test\"}}"
```

**Documentation:** [launcher/dashboard/README.md](launcher/dashboard/README.md)

---

### 3. Web Console

**Launcher:** `launcher/web/launcher_web.py`

**Port:** 9000 (default)

**Features:**
- Lightweight browser interface
- Quick operation execution
- Operation history
- Good for development/testing

**Example:**
```bash
# Start web console
launcher_web.bat --port 9000

# Access in browser
http://127.0.0.1:9000
```

**Documentation:** [launcher/web/README.md](launcher/web/README.md)

---

### 4. Flask Server

**Launcher:** `launcher/flask/launcher_flask.py`

**Port:** 5000 (default)

**Features:**
- Modern web framework
- Real-time updates via SocketIO
- Full-featured web application
- Best for production web interface

**Example:**
```bash
# Start Flask server
launcher_flask.bat --port 5000

# Access in browser
http://localhost:5000

# With debug mode
launcher_flask.bat --debug
```

**Documentation:** [launcher/flask/README.md](launcher/flask/README.md)

## Directory Structure

```
D:/Code/Project/
├── menu.bat                          # Main menu launcher
├── launcher/
│   ├── README.md                     # This file
│   ├── common/
│   │   ├── __init__.py
│   │   └── launcher_base.py          # Base launcher class
│   ├── cli/
│   │   ├── README.md
│   │   ├── launcher_cli.py
│   │   └── launcher_cli.bat
│   ├── dashboard/
│   │   ├── README.md
│   │   ├── launcher_dashboard.py
│   │   └── launcher_dashboard.bat
│   ├── web/
│   │   ├── README.md
│   │   ├── launcher_web.py
│   │   └── launcher_web.bat
│   └── flask/
│       ├── README.md
│       ├── launcher_flask.py
│       └── launcher_flask.bat
└── EE/                               # EE source code
    └── src/
        └── gateway/                  # UG implementation
```

## Gateway Operations

All interfaces provide access to the same gateway operations:

### Configuration (config)
```bash
# Get configuration
exec config.get --payload "{\"key\": \"app.name\"}"

# Set configuration
exec config.set --payload "{\"key\": \"app.debug\", \"value\": true}"

# List all configuration
exec config.get_all
```

### Security (security)
```bash
# Encrypt data
exec security.encrypt --payload "{\"data\": \"secret\"}"

# Decrypt data
exec security.decrypt --payload "{\"encrypted_data\": \"...\"}"

# Hash data
exec security.hash --payload "{\"data\": \"password\"}"
```

### Logging (logging)
```bash
# Log info message
exec logging.log.info --payload "{\"message\": \"Server started\"}"

# Log error message
exec logging.log.error --payload "{\"message\": \"Connection failed\"}"

# Set log level
exec logging.set_level --payload "{\"level\": \"DEBUG\"}"
```

### Metrics (metrics)
```bash
# Increment counter
exec metrics.counter.increment --payload "{\"name\": \"requests\", \"value\": 1}"

# Get statistics
exec metrics.get_stats
```

## Common Use Cases

### 1. Quick Command Execution
Use CLI for one-off commands:
```bash
launcher\cli\launcher_cli.bat exec config.get --payload "{\"key\": \"database.host\"}"
```

### 2. Interactive Development
Use Dashboard for interactive testing:
```bash
launcher\dashboard\launcher_dashboard.bat
# Open http://127.0.0.1:8080
```

### 3. Production API
Use Flask server for production:
```bash
launcher\flask\launcher_flask.bat --host 0.0.0.0 --port 5000
```

### 4. Quick Testing
Use Web Console for quick tests:
```bash
launcher\web\launcher_web.bat --port 9000
```

## Error Handling

All launchers provide consistent error handling:

- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 2**: Import error
- **Exit Code 3**: UG initialization failed
- **Exit Code 4**: Gateway not initialized
- **Exit Code 5**: Execution failed
- **Exit Code 130**: Interrupted by user (Ctrl+C)

## Development

### Adding a New Launcher

1. Create new directory under `launcher/`
2. Create `launcher_*.py` using `LauncherBase`
3. Create `launcher_*.bat` for Windows
4. Create `README.md` with documentation
5. Add entry to `menu.bat`

Example launcher:
```python
from launcher_common.launcher_base import LauncherBase

launcher = LauncherBase(name="MyLauncher")
gateway = launcher.initialize()
result = launcher.execute("config.get", {"key": "test"})
launcher.shutdown()
```

## Requirements

- Python 3.8+
- EE/src with gateway implementations
- Dependencies:
  - Flask (for Flask launcher)
  - Flask-SocketIO (for Flask launcher)
  - python-socketio (for Flask launcher)
  - eventlet or gevent (for Flask WebSocket)

## Security Notes

### Local Development
All launchers bind to `127.0.0.1` by default for security.

### External Access
To expose externally, use `--host 0.0.0.0`:
```bash
launcher_dashboard.bat --host 0.0.0.0 --port 8080
```

**WARNING**: When exposing externally:
1. Use appropriate firewall rules
2. Implement authentication
3. Use HTTPS in production
4. Restrict access to trusted networks
5. Keep dependencies updated

## Troubleshooting

### Port Already in Use
```
Error: [Errno 48] Address already in use
```
**Solution:** Use a different port:
```bash
launcher_dashboard.bat --port 8081
```

### Import Errors
```
ModuleNotFoundError: No module named 'EE.src.gateway'
```
**Solution:** Ensure you're running from the project root and EE/src exists.

### Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** May require admin privileges for ports < 1024, or use a higher port.

## License

Part of the EE (Enterprise Environment) project.

## See Also

- [EE/src/gateway/gateway.py](../EE/src/gateway/gateway.py) - UG implementation
- [EE/src/gateway/gateway_domains.py](../EE/src/gateway/gateway_domains.py) - Domain gateways
- [launcher/common/launcher_base.py](launcher/common/launcher_base.py) - Base launcher class
