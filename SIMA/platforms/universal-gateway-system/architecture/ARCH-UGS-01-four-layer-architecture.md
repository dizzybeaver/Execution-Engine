# ARCH-UGS-01: Four-Layer Architecture

## Metadata
- **Version**: 1.0.0
- **Date**: 2025-12-31
- **Purpose**: Define the core architectural layers of the Universal Gateway System
- **REF-ID**: ARCH-UGS-01
- **Status**: Active
- **Related**: DEC-UGS-01, DEC-UGS-02, GATE-UGS-01

## Architecture Overview

The Universal Gateway System implements a strict four-layer architecture that governs all cross-component operations. Each layer has specific responsibilities and strict boundaries.

### The Four Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Application Layer                                  │
│ - Business logic and orchestration                          │
│ - Initiates operations through UG                           │
└────────────────────┬────────────────────────────────────────┘
                     │ execute_operation(route, payload)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Universal Gateway (UG)                             │
│ - Single execution authority                                │
│ - Route resolution and validation                           │
│ - Centralized error handling and monitoring                 │
└────────────────────┬────────────────────────────────────────┘
                     │ Route to domain gateway
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Domain Gateways                                    │
│ - Domain-specific routing and coordination                  │
│ - Interface selection and invocation                        │
│ - Domain-level policy enforcement                           │
└────────────────────┬────────────────────────────────────────┘
                     │ Delegate to interface
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Interfaces and Factories                           │
│ - Interfaces: Isolated capability modules                   │
│ - Factories: Concrete execution units                       │
│ - Pure business logic implementation                        │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Layer 1: Application Layer

**Purpose**: Business logic and workflow orchestration

**Responsibilities**:
- Implementing business processes and workflows
- Coordinating multiple operations through UG
- Application-level validation and logic
- User interaction and API endpoints

**Rules**:
- NEVER bypass UG for cross-component operations
- May use local components directly without UG
- All cross-domain requests must go through UG

**Example Operations**:
- User request handling
- Business process orchestration
- Multi-step workflows
- External API integration

### Layer 2: Universal Gateway (UG)

**Purpose**: Central execution authority and platform coordinator

**Responsibilities**:
- Single entry point for all cross-component operations
- Route resolution and validation
- Centralized error handling
- Platform-level monitoring and logging
- Access control enforcement

**Rules**:
- NO business logic (only routing and coordination)
- NO direct database or external system access
- MUST delegate all work to domain gateways
- MUST maintain operation registry

**Key Capability**: `execute_operation(route, payload)`

### Layer 3: Domain Gateways

**Purpose**: Domain-specific routing and interface coordination

**Responsibilities**:
- Route operations within a domain
- Select appropriate interfaces for operations
- Coordinate multiple interfaces if needed
- Domain-level validation and policies
- Aggregate results from interfaces

**Rules**:
- Each gateway handles one domain (e.g., Network, Storage, Security)
- Cannot directly call other domain gateways
- Must maintain domain dispatch dictionaries
- Enforce interface isolation rules

**Examples**:
- NetworkGateway: Routes network-related operations
- StorageGateway: Manages storage operations
- SecurityGateway: Handles security and authorization

### Layer 4: Interfaces and Factories

**Purpose**: Concrete capability implementation

**Interface Responsibilities**:
- Implement specific capabilities (e.g., HTTP client, file storage)
- Validate and transform inputs
- Handle domain-specific logic
- Maintain isolation (no external imports)

**Factory Responsibilities**:
- Create and configure concrete implementations
- Manage resource lifecycle
- Provide execution units to interfaces
- Encapsulate complex object creation

**Rules**:
- Interfaces cannot import outside their package
- Factories are the actual execution units
- No direct invocation by application layer
- Pure business logic, no routing concerns

## Execution Flow

### Standard Operation Flow

```
1. Application Layer
   └─ Initiates: UG.execute_operation("network/http/get", {url, headers})

2. Universal Gateway
   ├─ Validates route format
   ├─ Resolves: "network" → NetworkGateway
   ├─ Validates permissions
   └─ Delegates: NetworkGateway.execute("http/get", payload)

3. Domain Gateway (NetworkGateway)
   ├─ Parses operation: "http/get"
   ├─ Consults DISPATCH dictionary
   ├─ Selects: HttpInterface.get()
   └─ Delegates: HttpInterface.get(url, headers)

4. Interface (HttpInterface)
   ├─ Validates parameters
   ├─ Invokes factory method
   └─ Returns result

5. Return Path
   Interface → Domain Gateway → Universal Gateway → Application
```

### Error Handling Flow

```
Error occurs at Layer 4 (Interface)
    ↓
Interface catches and wraps error
    ↓
Domain Gateway adds domain context
    ↓
Universal Gateway applies platform error handling
    ↓
Application receives standardized error response
```

## Layer Boundaries

### Strict Boundaries

**Layer 1 → Layer 2**
- Only through `UG.execute_operation()`
- No direct access to lower layers
- Cannot bypass gateway

**Layer 2 → Layer 3**
- Only through domain gateway delegation
- UG cannot skip to Layer 4
- No inter-gateway communication

**Layer 3 → Layer 4**
- Only through interface invocation
- No direct factory calls
- Interface isolation enforced

### Cross-Layer Communication

**Permitted Patterns**:
- Sequential layer traversal (1→2→3→4)
- Return path following layers in reverse
- Error propagation up through layers

**Prohibited Patterns**:
- Skipping layers (e.g., Layer 1 → Layer 4)
- Direct horizontal communication (e.g., Gateway → Gateway)
- Layer inversion (lower layer calling upper)

## Benefits

### Architectural Clarity
- Clear separation of concerns
- Each layer has single, well-defined purpose
- Easy to understand and communicate

### Independent Evolution
- Layers can evolve independently
- Changes in one layer don't cascade to others
- Simplified maintenance and upgrades

### Testability
- Each layer tested in isolation
- Mock dependencies at layer boundaries
- Clear testing responsibilities

### Scalability
- Different layers can scale independently
- Optimization targeted at specific layers
- Bottlenecks easily identified

## Implementation Guidelines

### Layer Identification
- Ask: "Does this belong in routing or business logic?"
- Routing → Layers 2 or 3
- Business logic → Layers 1 or 4

### Boundary Enforcement
- Use static analysis to detect layer violations
- Architectural review for cross-layer code
- Automated testing for boundary compliance

### Layer Responsibilities
- Document each layer's specific responsibilities
- Train teams on layer boundaries
- Code review checklist includes layer verification

## Validation Criteria

### Structural Validation
- Import graph follows layer hierarchy
- No circular dependencies between layers
- Clear ownership of each component

### Behavioral Validation
- Execution flow respects layer boundaries
- Error handling propagates correctly
- No layer-skipping in operations

## Related Decisions

- **DEC-UGS-01**: Single Execution Authority (UG as Layer 2)
- **DEC-UGS-02**: Interface Isolation (Layer 4 constraints)
- **GATE-UGS-01**: Domain Gateway Pattern (Layer 3 details)
- **GATE-UGS-02**: DISPATCH Dictionary Pattern (Routing implementation)

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-31 | Initial | Initial architecture document |

