# EE CLI Gateway - Command Line Interface

Complete CLI implementation for the EE Universal Gateway System.

## Overview

The CLI Gateway provides a comprehensive command-line interface for interacting
with all EE domain gateways. It supports both standalone CLI usage and
programmatic integration.

## Architecture

```
User Command
    ↓
CLI Parser (cli_parser.py)
    ↓
CLI Executor (cli_executor.py)
    ↓
Gateway Router (gateway_router.py)
    ↓
Domain Gateway (gateway_domains.py)
    ↓
Implementation
```

## Components

### 1. **cli_common.py** - Common Utilities
- `CLIGatewayError`: Base exception for CLI errors
- `CLIValidationError`: Input validation errors
- `CLIExecutionError`: Command execution errors

### 2. **cli_parser.py** - Argument Parser
- Parses CLI commands and arguments
- Supports multiple subcommands
- Validates input format

**Available Commands:**
- `list-all`: List all domains and operations
- `list-domains`: List all registered domains
- `list-routes [--domain <name>]`: List all routes (optional domain filter)
- `exec <route> [--payload <json>]`: Execute a gateway route
- `stats`: Get gateway statistics

**Global Options:**
- `--json`: Format output as JSON

### 3. **cli_executor.py** - Command Executor
- Executes parsed CLI commands
- Delegates to gateway router
- Handles errors gracefully

### 4. **cli_output.py** - Output Renderer
- Formats command results
- Supports text and JSON output
- Pretty-prints dictionaries and lists

### 5. **unified_cli.py** - Main CLI Interface
- Integrates all CLI components
- Provides simple API for CLI execution
- Entry point for standalone usage

### 6. **cli_gateway.py** - CLI Domain Gateway
- Exposes CLI operations through gateway interface
- Enables programmatic CLI execution
- Integrates with gateway registry

## Usage Examples

### Standalone CLI Usage

```python
from gateway.cli import create_cli_gateway

# Create CLI instance
cli = create_cli_gateway()

# List all domains
cli.run(["list-domains"])
# Output:
# config
# security
# logging
# metrics
# debug
# serialization
# cli

# List all routes
cli.run(["list-routes"])

# Execute a route
cli.run(["exec", "config.get", "--payload", '{"key": "database.host"}'])

# Get statistics
cli.run(["stats"])

# JSON output
cli.run(["--json", "list-domains"])
```

### Programmatic Usage

```python
from gateway.cli import CLIExecutor, CLIArgs
from gateway.gateway import get_unified_router

# Create executor
gateway = get_unified_router()
executor = CLIExecutor(gateway=gateway)

# Execute commands programmatically
args = CLIArgs(command="list-domains")
result = executor.execute(args)
print(result)  # ['config', 'security', 'logging', ...]

# Execute routes
args = CLIArgs(
    command="exec",
    route="config.get",
    payload='{"key": "database.host"}'
)
result = executor.execute(args)
```

### Gateway Integration

```python
from gateway.gateway import execute

# List CLI operations
result = execute("cli.list_all", {})

# List available CLI commands
result = execute("cli.list_commands", {})
print(result["commands"])  # {'list-all', 'list-domains', 'exec', ...}

# Parse CLI arguments
result = execute("cli.parse_args", {
    "args": ["exec", "config.get", "--payload", '{"key": "test"}']
})
print(result["command"])  # "exec"
print(result["route"])  # "config.get"

# Run CLI command programmatically
result = execute("cli.run", {
    "args": ["list-domains"]
})
print(result["exit_code"])  # 0
print(result["output"])  # "config\nsecurity\n..."
```

## CLI Commands

### list-all
List all domains and their complete operation details.

```bash
ee-gateway list-all
```

### list-domains
List all registered domain names.

```bash
ee-gateway list-domains
```

### list-routes
List all available routes across all domains.

```bash
# List all routes
ee-gateway list-routes

# Filter by domain
ee-gateway list-routes --domain config
```

### exec
Execute a specific gateway route.

```bash
# Basic execution
ee-gateway exec config.get

# With payload
ee-gateway exec config.get --payload '{"key": "database.host"}'

# With JSON output
ee-gateway --json exec security.auth.authenticate --payload '{"user": "admin"}'
```

### stats
Get gateway usage and performance statistics.

```bash
ee-gateway stats
```

## Output Formats

### Text Output (Default)
Human-readable, indented text format.

```bash
$ ee-gateway list-domains
config
security
logging
metrics
debug
serialization
cli
```

### JSON Output
Machine-readable JSON format.

```bash
$ ee-gateway --json list-domains
{
  "domains": [
    "config",
    "security",
    "logging",
    "metrics",
    "debug",
    "serialization",
    "cli"
  ]
}
```

## CLI Domain Gateway Routes

The CLI gateway exposes these routes through the gateway system:

- **cli.run**: Run CLI command programmatically
  - Parameters: `args` (list of command-line arguments)
  - Returns: `{exit_code, output, error}`

- **cli.list_commands**: List all available CLI commands
  - Parameters: None
  - Returns: `{commands: {...}, total: n}`

- **cli.parse_args**: Parse CLI arguments without executing
  - Parameters: `args` (list of command-line arguments)
  - Returns: `{command, route, payload, json_output, domain}`

- **cli.list_all**: List all CLI operations
  - Parameters: None
  - Returns: CLI domain metadata

## Integration Status

✅ **COMPLETE** - All components implemented and integrated:

1. ✅ **cli/__init__.py** - Package initialization with exports
2. ✅ **cli/cli_common.py** - Common utilities and exceptions
3. ✅ **cli/cli_parser.py** - CLI argument parser
4. ✅ **cli/cli_executor.py** - CLI command executor
5. ✅ **cli/cli_output.py** - CLI output formatter
6. ✅ **cli/unified_cli.py** - Unified CLI interface
7. ✅ **cli/cli_gateway.py** - CLI domain gateway
8. ✅ **Gateway registration** - CLI domain registered in gateway.py
9. ✅ **Test script** - Comprehensive test suite

## Files Created

- `D:\Code\Project\EE\src\gateway\cli\__init__.py`
- `D:\Code\Project\EE\src\gateway\cli\cli_common.py`
- `D:\Code\Project\EE\src\gateway\cli\cli_parser.py`
- `D:\Code\Project\EE\src\gateway\cli\cli_executor.py`
- `D:\Code\Project\EE\src\gateway\cli\cli_output.py`
- `D:\Code\Project\EE\src\gateway\cli\unified_cli.py`
- `D:\Code\Project\EE\src\gateway\cli\cli_gateway.py`
- `D:\Code\Project\EE\src\gateway\cli\test_cli_gateway.py`
- `D:\Code\Project\EE\src\gateway\cli\README.md`

## Testing

Run the test script to verify CLI gateway functionality:

```bash
cd D:\Code\Project\EE\src\gateway\cli
python test_cli_gateway.py
```

## Next Steps

1. **Create console script entry point** in pyproject.toml:
   ```toml
   [project.scripts]
   ee-gateway = "gateway.cli.unified_cli:main"
   ```

2. **Add shell completion** for better UX

3. **Add color output** for text format (optional)

4. **Add interactive mode** for REPL-style usage (optional)

## References

Based on CLI Gateway pattern from:
- `D:\Code\Project\Gateway\CLI\cli_common.py`
- `D:\Code\Project\Gateway\CLI\cli_parser.py`
- `D:\Code\Project\Gateway\CLI\cli_executor.py`
- `D:\Code\Project\Gateway\CLI\cli_output.py`
- `D:\Code\Project\Gateway\CLI\unified_cli.py`
