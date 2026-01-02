# EE Doc Gateway

Documentation gateway for the EE Universal Gateway system.

## Overview

The Doc Gateway provides automated documentation generation for all EE gateway components, including:
- Commands documentation
- Routes documentation
- Services documentation
- Schemas documentation

## Architecture

```
Doc Gateway
├── doc_common.py          # Common utilities and exceptions
├── doc_command.py         # Command documentation generator
├── doc_route.py           # Route documentation generator
├── doc_service.py         # Service documentation generator
├── doc_schema.py          # Schema documentation generator
├── unified_doc_generator.py  # Unified documentation generator
└── doc_gateway.py         # Doc domain gateway
```

## Usage

### Basic Usage

```python
from gateway.gateway_registry import EEDomainRegistry
from gateway.doc import create_doc_generator

# Get registry
registry = EEDomainRegistry.get_instance()

# Create doc generator
generator = create_doc_generator(
    gateway_registry=registry,
    output_dir="./docs",
    formats=["markdown", "html", "json"]
)

# Generate all documentation
result = generator.generate_all()
print(result)
```

### Gateway Integration

```python
from gateway.gateway_registry import EEDomainRegistry

# Get registry
registry = EEDomainRegistry.get_instance()

# Get doc gateway
doc_gateway = registry.get("doc")

# Generate command documentation
result = doc_gateway.execute("doc.generate.commands", {
    "output_dir": "./docs",
    "format": "markdown"
})

# Generate all documentation
result = doc_gateway.execute("doc.generate.all", {
    "output_dir": "./docs",
    "formats": ["markdown", "html"]
})
```

## Components

### DocGatewayDomain

Domain gateway that integrates documentation generation with the EE gateway system.

**Routes:**
- `doc.generate.commands` - Generate command documentation
- `doc.generate.routes` - Generate route documentation
- `doc.generate.services` - Generate service documentation
- `doc.generate.schemas` - Generate schema documentation
- `doc.generate.all` - Generate all documentation
- `doc.generate.merged` - Generate merged documentation
- `doc.list_all` - List all doc operations

### UnifiedDocGenerator

Orchestrates all documentation generators and provides a single interface for generating comprehensive documentation.

**Methods:**
- `generate_all()` - Generate all documentation
- `generate_commands()` - Generate command documentation
- `generate_routes()` - Generate route documentation
- `generate_services()` - Generate service documentation
- `generate_schemas()` - Generate schema documentation
- `generate_merged()` - Generate merged documentation

### Individual Generators

Each generator can be used independently:

- **CommandDocGenerator** - Generate command documentation
- **RouteDocGenerator** - Generate route documentation
- **ServiceDocGenerator** - Generate service documentation
- **SchemaDocGenerator** - Generate schema documentation

## Output Formats

### Markdown

Standard Markdown format with tables for parameters, fields, and examples.

```python
generator.generate_markdown()
```

### JSON

Structured JSON format for programmatic processing.

```python
generator.generate_json()
```

### HTML

Styled HTML documentation with CSS formatting.

```python
generator.generate_html()
```

## Configuration

### DocGenerationConfig

```python
from gateway.doc import DocGenerationConfig

config = DocGenerationConfig(
    output_dir="./docs",
    formats=["markdown", "html"],
    include_commands=True,
    include_routes=True,
    include_services=True,
    include_schemas=True,
    merge_single_file=False
)
```

## Examples

### Generate Command Documentation

```python
from gateway.doc import CommandDocGenerator

generator = CommandDocGenerator(registry)
docs = generator.generate_markdown()

# Save to file
generator.save_documentation("./docs/commands.md", "markdown")
```

### Generate All Documentation

```python
from gateway.doc import create_doc_generator

generator = create_doc_generator(registry, output_dir="./docs")
result = generator.generate_all()

for gen_result in result["generated"]:
    for file_path in gen_result["files"]:
        print(f"Generated: {file_path}")
```

### Generate Merged Documentation

```python
config = DocGenerationConfig(
    output_dir="./docs",
    formats=["markdown"],
    merge_single_file=True
)

generator = UnifiedDocGenerator(registry, config)
result = generator.generate_merged()

# Single file with all documentation
```

## Error Handling

```python
from gateway.doc import DocGatewayError, DocGenerationError

try:
    generator.generate_all()
except DocGenerationError as e:
    print(f"Generation failed: {e}")
except DocGatewayError as e:
    print(f"Gateway error: {e}")
```

## Integration with EE Gateway

The Doc Gateway is automatically registered with the EE gateway system:

```python
from gateway.gateway_registry import EEDomainRegistry

registry = EEDomainRegistry.get_instance()

# Doc gateway is available
doc_gateway = registry.get("doc")

# List all domains
print(registry.list_domains())  # ['config', 'security', ..., 'doc']
```

## Based On

This implementation is based on the Documentation Gateway pattern from:
`D:\Code\Project\Gateway\Doc\`
