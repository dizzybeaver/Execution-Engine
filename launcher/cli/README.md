# EE CLI Launcher

Command-Line Interface launcher for EE using the Unified Gateway (UG).

## Usage

### Direct Python Execution

```bash
python launcher_cli.py [args]
```

### Windows Batch File

```cmd
launcher_cli.bat [args]
```

## Common Commands

### List All Available Domains

```bash
python launcher_cli.py list-domains
```

Output:
```
config
security
logging
metrics
debug
serialization
cli
doc
isp
test
```

### Execute Gateway Operations

```bash
# Get configuration value
python launcher_cli.py exec config.get --payload '{"key": "database.host"}'

# Encrypt data
python launcher_cli.py exec security.encrypt --payload '{"data": "sensitive", "algorithm": "aes"}'

# Log message
python launcher_cli.py exec logging.log.info --payload '{"message": "Hello from CLI"}'
```

### JSON Output Format

```bash
python launcher_cli.py --json exec config.get --payload '{"key": "test"}'
```

Output:
```json
{
  "result": "config_value_for_test"
}
```

### Get Gateway Statistics

```bash
python launcher_cli.py stats
```

## CLI Gateway Routes

The CLI launcher uses the UG CLI gateway which provides:

- **list-domains**: List all registered domain gateways
- **list-operations**: List all operations in a domain
- **exec**: Execute a gateway route
- **stats**: Get gateway statistics
- **help**: Show help information

## Examples

### Configuration Operations

```bash
# Get configuration
python launcher_cli.py exec config.get --payload '{"key": "app.name"}'

# Set configuration
python launcher_cli.py exec config.set --payload '{"key": "app.debug", "value": true}'

# List all config
python launcher_cli.py exec config.get_all
```

### Security Operations

```bash
# Authenticate
python launcher_cli.py exec security.auth.authenticate --payload '{"credentials": {"user": "admin", "pass": "secret"}}'

# Encrypt data
python launcher_cli.py exec security.encrypt --payload '{"data": "secret"}'

# Hash data
python launcher_cli.py exec security.hash --payload '{"data": "password"}'
```

### Logging Operations

```bash
# Log info
python launcher_cli.py exec logging.log.info --payload '{"message": "Server started"}'

# Log error
python launcher_cli.py exec logging.log.error --payload '{"message": "Connection failed"}'

# Set log level
python launcher_cli.py exec logging.set_level --payload '{"level": "DEBUG"}'
```

### Metrics Operations

```bash
# Increment counter
python launcher_cli.py exec metrics.counter.increment --payload '{"name": "requests", "value": 1}'

# Get statistics
python launcher_cli.py exec metrics.get_stats
```

## Architecture

```
CLI Launcher
    ↓ (initialize UG)
Unified Gateway (UG)
    ↓ (route operations)
Domain Gateways (config, security, logging, etc.)
    ↓ (implement)
EE Functionality
```

## Error Handling

The launcher provides professional error handling:

- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 2**: Import error
- **Exit Code 3**: UG initialization failed
- **Exit Code 4**: Gateway not initialized
- **Exit Code 5**: Execution failed
- **Exit Code 6**: List operations failed
- **Exit Code 7**: Get stats failed
- **Exit Code 130**: Interrupted by user (Ctrl+C)

## Development

The launcher uses ONLY UG for all operations:

- No code reimplementations
- All operations go through `gateway.execute()`
- Professional error handling via `LauncherBase`
- Path setup for Lambda compatibility

## See Also

- [../common/launcher_base.py](../common/launcher_base.py) - Base launcher class
- [../../EE/src/gateway/gateway.py](../../EE/src/gateway/gateway.py) - UG implementation
- [../../EE/src/gateway/cli/](../../EE/src/gateway/cli/) - CLI gateway implementation
