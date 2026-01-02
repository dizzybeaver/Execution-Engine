# GATE-UGS-02: DISPATCH Dictionary Pattern

## Metadata
- **Version**: 1.0.0
- **Date**: 2025-12-31
- **Purpose**: Define the DISPATCH dictionary pattern for O(1) operation routing
- **REF-ID**: GATE-UGS-02
- **Status**: Active
- **Related**: GATE-UGS-01, DEC-UGS-01, ARCH-UGS-01

## Pattern Overview

The DISPATCH dictionary pattern provides constant-time (O(1)) operation routing by mapping operation names to their concrete implementations. It serves as the routing engine for Domain Gateways.

### Pattern Definition

A DISPATCH dictionary is a mapping structure where:
- **Keys**: Operation name strings (e.g., "http/get", "file/read")
- **Values**: Concrete implementation targets (interface methods)
- **Lookup**: Constant-time dictionary access
- **Documentation**: Self-documenting through operation visibility

### Core Benefits

**Performance**
- O(1) operation resolution
- No conditional chains or if-else ladders
- Minimal routing overhead

**Maintainability**
- Self-documenting operation catalog
- Single source of truth for available operations
- Easy to add/remove operations

**Reliability**
- No operation key collisions
- Fail-fast on unknown operations
- Type-safe target references

## Pattern Structure

### Basic DISPATCH Structure

```
DISPATCH = {
    # Operation Name → Implementation Target
    "operation/name": TargetInterface.method,
    "domain/sub-operation": AnotherInterface.method,
    "resource/action": ThirdInterface.method,
}
```

### Key Components

#### 1. Operation Name (Key)
**Format**: Hierarchical string with forward slashes

**Convention**:
```
domain/category/action
Examples:
- "network/http/get"
- "storage/file/read"
- "security/auth/validate"
```

**Rules**:
- Use lowercase
- Separate levels with forward slash
- Be descriptive and specific
- Avoid abbreviations

#### 2. Implementation Target (Value)
**Format**: Direct reference to interface method

**Types**:
- Bound method: `InterfaceClass.method`
- Lambda wrapper: `lambda p: Interface.method(p)`
- Function reference: `module.function`

#### 3. DISPATCH Dictionary
**Container**: Hash map / dictionary / associative array

**Location**: Defined within Domain Gateway class
**Access**: Private constant or class attribute

## Routing Flow

### Standard Routing

```
1. Gateway receives operation: "http/get"
2. Gateway looks up: DISPATCH.get("http/get")
3. Result: HttpInterface.get method reference
4. Gateway invokes: method_reference(payload)
5. Return: Result to Universal Gateway
```

### Unknown Operation Handling

```
1. Gateway receives operation: "unknown/op"
2. Gateway looks up: DISPATCH.get("unknown/op")
3. Result: None (key not found)
4. Gateway raises: OperationNotRegistered
5. Universal Gateway handles error
```

### Fallback Routing (Optional)

```
1. Gateway receives operation: "http/custom"
2. Primary lookup: DISPATCH.get("http/custom")
3. Result: None
4. Fallback lookup: DISPATCH.get("http/*")
5. Result: HttpInterface.generic_handler
6. Gateway invokes fallback handler
```

## Implementation Patterns

### Pattern 1: Direct Method Reference
```
DISPATCH = {
    "http/get": HttpInterface.get,
    "http/post": HttpInterface.post,
}

# Usage
method = DISPATCH["http/get"]
result = method(payload)
```

**Pros**:
- Fastest lookup
- No indirection
- Simple syntax

**Cons**:
- Cannot pass additional parameters
- Less flexible for complex routing

### Pattern 2: Lambda Wrapper
```
DISPATCH = {
    "http/get": lambda p: HttpInterface.get(p),
    "http/post": lambda p: HttpInterface.post(p),
    "batch/insert": lambda p: BatchInterface.insert(p, async=True),
}

# Usage
handler = DISPATCH["batch/insert"]
result = handler(payload)
```

**Pros**:
- Can add parameters
- Transform payload before invocation
- Wrap with additional logic

**Cons**:
- Slight overhead from lambda
- Debugging stack traces longer

### Pattern 3: Class Method Dispatch
```
DISPATCH = {
    "http/get": (HttpInterface, "get"),
    "http/post": (HttpInterface, "post"),
}

# Usage
interface_class, method_name = DISPATCH["http/get"]
method = getattr(interface_class, method_name)
result = method(payload)
```

**Pros**:
- Supports lazy interface initialization
- Clear separation of class and method
- Easier for dynamic loading

**Cons**:
- Requires getattr() call
- More lookup steps

## Operation Naming Conventions

### Hierarchical Structure

```
domain/category/action
│    │        │
│    │        └─ Specific operation (verb)
│    └─ Capability or resource type
└─ Domain identifier
```

### Examples by Domain

**Network Domain**
```
"network/http/get"
"network/http/post"
"network/http/delete"
"network/ws/connect"
"network/tcp/open"
```

**Storage Domain**
```
"storage/file/read"
"storage/file/write"
"storage/database/query"
"storage/cache/get"
"storage/blob/upload"
```

**Security Domain**
```
"security/auth/validate"
"security/auth/refresh"
"security/crypto/encrypt"
"security/acl/check"
```

### Naming Best Practices

**DO**:
- Use descriptive, specific names
- Follow verb/noun pattern
- Maintain consistent hierarchy
- Use lowercase only
- Separate with forward slashes

**DON'T**:
- Use abbreviations (get vs retrieve)
- Mix naming conventions
- Use underscores instead of slashes
- Create overly generic names

## Advanced Patterns

### Pattern 1: Namespace Prefixing
```
# Gateway handles multiple namespaces
DISPATCH = {
    "v1/http/get": HttpInterface.get_v1,
    "v2/http/get": HttpInterface.get_v2,
    "beta/http/get": HttpInterface.get_beta,
}
```

### Pattern 2: Composite Operations
```
# Operation that coordinates multiple interfaces
DISPATCH = {
    "sync/full": lambda p: CompositeInterface.full_sync(p),
    "backup/create": lambda p: BackupInterface.create(p),
}
```

### Pattern 3: Dynamic Registration
```
# Runtime operation registration
class Gateway:
    def __init__(self):
        self.DISPATCH = {}

    def register_operation(self, name, handler):
        self.DISPATCH[name] = handler

# Usage
gateway.register_operation("custom/op", CustomHandler.handle)
```

## Performance Characteristics

### Time Complexity
- **Best Case**: O(1) - Direct hash map lookup
- **Average Case**: O(1) - Hash map lookup
- **Worst Case**: O(n) - Hash collision (extremely rare)

### Space Complexity
- O(n) where n = number of operations
- Linear growth with operation count
- Minimal per-entry overhead

### Optimization Techniques

**1. String Interning**
- Intern operation names during initialization
- Reduces string comparison overhead
- Improves hash computation

**2. Dispatch Caching**
- Cache frequently used lookups
- Avoid repeated dictionary access
- Monitor cache hit rates

**3. Lazy Loading**
- Load operation handlers on first use
- Reduce initialization time
- Trade memory for startup speed

## Error Handling

### Unknown Operation
```
Operation requested: "unknown/op"
Key not found in DISPATCH

Action: Raise OperationNotRegistered
Context: Gateway name, operation name
Recovery: None (fail-fast)
```

### Target Not Callable
```
DISPATCH["bad/op"] = "not_a_method"

Action: Raise InvalidDispatchTarget
Context: Operation name, target type
Recovery: None (configuration error)
```

### Handler Exception
```
Handler raises exception during execution

Action: Catch and wrap in GatewayError
Context: Operation name, original exception
Recovery: Return error result to UG
```

## Testing Strategies

### Unit Testing DISPATCH

**Test Coverage**:
- All operations in DISPATCH map to valid targets
- Unknown operations raise appropriate errors
- Operation handlers are callable
- Performance benchmarks for lookup

**Example Tests**:
```
1. Verify operation exists: assert "op/name" in DISPATCH
2. Verify target is callable: assert callable(DISPATCH["op"])
3. Verify unknown operation raises: gateway.execute("unknown")
4. Benchmark lookup time: timeit(DISPATCH.get)
```

### Integration Testing

**Test Scenarios**:
- Execute each operation through gateway
- Verify correct handler invoked
- Test error propagation
- Measure end-to-end latency

## Documentation Aspects

### Self-Documenting Properties

DISPATCH serves as living documentation:
- All operations visible in one place
- Operation naming convention enforced
- Handler relationships clear
- Domain boundaries explicit

### Documentation Generation

**Automated Docs**:
- Parse DISPATCH dictionaries
- Generate operation catalog
- Extract parameter schemas
- Create API reference documentation

**Manual Docs**:
- Group related operations
- Add usage examples
- Document operation semantics
- Provide context for each operation

## Migration Strategies

### Migrating to DISPATCH Pattern

**From Conditional Chains**:
```
# Before
if operation == "http/get":
    return HttpInterface.get(payload)
elif operation == "http/post":
    return HttpInterface.post(payload)
else:
    raise UnknownOperation(operation)

# After
DISPATCH = {
    "http/get": HttpInterface.get,
    "http/post": HttpInterface.post,
}
handler = DISPATCH.get(operation)
if not handler:
    raise UnknownOperation(operation)
return handler(payload)
```

## Best Practices Summary

### DO
- Use descriptive, hierarchical operation names
- Keep DISPATCH as class constant
- Register all operations during initialization
- Validate operation targets on startup
- Document operation semantics
- Profile DISPATCH performance
- Use type hints for targets

### DON'T
- Modify DISPATCH at runtime (except dynamic registration)
- Use generic operation names
- Allow duplicate keys
- Bypass DISPATCH for any operation
- Mix operation naming conventions
- Embed business logic in DISPATCH values

## Related Patterns

- **GATE-UGS-01**: Domain Gateway Pattern (container for DISPATCH)
- **ARCH-UGS-01**: Four-Layer Architecture (routing context)
- **DEC-UGS-01**: Single Execution Authority (UG routing)

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-31 | Initial | Initial pattern documentation |

