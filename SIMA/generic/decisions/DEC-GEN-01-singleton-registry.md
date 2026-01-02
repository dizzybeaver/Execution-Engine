# DEC-GEN-01: Singleton Registry Pattern

**Status**: Active
**Category**: Architecture Decision
**Source**: EE Codebase Analysis
**Created**: 2025-12-31

## Context

In many systems, certain resources or components need to be shared across the entire application. These include configuration managers, connection pools, logging systems, and other global services. Multiple instances can cause:

- Resource waste (duplicate connections, memory usage)
- Inconsistency (different instances with different state)
- Race conditions (concurrent access to multiple instances)
- Configuration drift (settings not synchronized)

## Decision

Use thread-safe singleton registry pattern with double-check locking to manage shared components. The registry provides a single source of truth for each component type while ensuring thread safety and lazy initialization.

## The Pattern

### What is a Singleton Registry?

A singleton registry is a centralized component that manages exactly one instance of each registered component type. It ensures:
- Only one instance exists per component type
- Instance is created lazily when first needed
- Thread-safe initialization and access
- Global accessibility throughout application

### Thread Safety with Double-Check Locking

Double-check locking optimizes thread safety by minimizing lock contention:
1. First check: Verify instance exists without locking (fast path)
2. Lock acquisition: Only if instance doesn't exist
3. Second check: Verify instance still doesn't exist (another thread may have created it)
4. Instance creation: Create and store instance
5. Lock release: Allow other threads to proceed

This pattern ensures:
- Only one thread creates the instance
- Other threads wait only during creation
- After creation, no locking overhead

## Benefits

### 1. Single Source of Truth
- All components access same instance
- Consistent state across application
- No synchronization issues between instances
- Predictable behavior

### 2. Thread Safety
- Safe concurrent access from multiple threads
- No race conditions during initialization
- No data corruption from simultaneous updates
- Reliable behavior in multi-threaded environments

### 3. Resource Efficiency
- Only one instance consumes resources
- Avoids duplicate connections, memory, handles
- Reduces application footprint
- Improves performance through reuse

### 4. Lazy Initialization
- Instance created only when needed
- Faster application startup
- Avoids creating unused components
- Reduces initial memory footprint

### 5. Global Access Point
- Easy to access from anywhere in code
- Centralized management of shared components
- Consistent access pattern
- Simplifies dependency management

## Implementation Considerations

### Thread Safety Requirements

**Required when**:
- Application uses multiple threads
- Singleton can be accessed concurrently
- Initialization is not atomic
- State can be modified after creation

**Thread safety strategies**:
- Double-check locking (balanced performance/safety)
- Static initialization (simplest, if language supports)
- Atomic operations (modern languages with built-in atomics)
- Synchronized access (simple but can be slow)

### Memory Model Awareness

Consider language-specific memory model guarantees:
- Visibility: When do other threads see changes?
- Ordering: Do operations maintain expected order?
- Publication: Is object fully constructed before visible?
- Reordering: Can compiler/CPU reorder operations?

### Lifecycle Management

**Singleton lifecycle**:
- **Initialization**: When and how is instance created?
- **Access**: How do components get the instance?
- **Shutdown**: When and how is instance destroyed?
- **Reinitialization**: Can singleton be reset (testing, reconfiguration)?

**Best practices**:
- Initialize once, use forever (simplest)
- Provide shutdown/cleanup for resource management
- Consider testing needs (reset between tests)
- Document thread safety guarantees

### Error Handling

**Initialization failures**:
- Fail fast and clearly
- Don't store partially-initialized instances
- Provide meaningful error messages
- Consider retry strategies for transient failures

**Runtime errors**:
- Distinguish between singleton errors and component errors
- Log errors with context
- Provide recovery mechanisms if appropriate
- Don't let singleton enter invalid state

## When to Use

### Ideal Situations
- Sharing expensive resources (database connections, thread pools)
- Coordinating global state (configuration, caching)
- Implementing central services (logging, metrics, event bus)
- Ensuring consistent behavior across application

### When to Avoid
- When multiple instances are beneficial (test isolation, different configurations)
- When initialization is complex and better done explicitly
- When components should be independent and not share state
- When dependency injection provides better alternative

## Alternatives

### Dependency Injection with Singleton Scope
- DI container manages single instance
- More flexible and testable
- Framework handles lifecycle and threading
- **Better when**: Using DI framework, want testability

### Service Locator Pattern
- Registry that provides any requested service
- Similar to singleton registry but more general
- **Better when**: Need dynamic service lookup, plugin architecture

### Explicit Dependency Passing
- Pass shared instances explicitly to components
- More verbose but clearer dependencies
- **Better when**: Want explicit dependencies, avoiding global state

### Application-Level Container
- Single container holds all shared components
- Container manages lifecycle and dependencies
- **Better when**: Many shared components with complex relationships

## Common Pitfalls

### Hidden Dependencies
- Components access singleton without declaring dependency
- Difficult to track what uses what
- Harder to test and reason about
- **Solution**: Make dependencies explicit through parameters

### Global State
- Singleton becomes dumping ground for global variables
- Creates implicit coupling between components
- Makes code harder to understand and test
- **Solution**: Limit singletons to true shared resources only

### Testing Challenges
- Singletons maintain state between tests
- Tests can interfere with each other
- Difficult to isolate test scenarios
- **Solution**: Provide reset mechanism or use dependency injection in tests

### Premature Optimization
- Using singleton before proving multiple instances are a problem
- Adds complexity for no benefit
- **Solution**: Start with explicit instantiation, optimize only if needed

### Thread Safety Oversights
- Assuming thread safety without proper implementation
- Language-specific nuances catch developers unaware
- **Solution**: Study language memory model, use proven patterns

## Testing Strategies

### Unit Testing
- Mock or stub singleton in tests
- Use dependency injection to substitute test doubles
- Test components in isolation from singleton
- Verify correct interaction patterns

### Integration Testing
- Test singleton with real dependencies
- Verify thread safety under concurrent load
- Test initialization and lifecycle
- Verify resource cleanup

### State Management
- Provide reset or reinitialize method for testing
- Use test-specific configuration
- Ensure tests don't affect each other
- Clean up resources after tests

## Cross-References

### Python/EE Implementation
- EE codebase GatewayRegistry as singleton registry
- Manages one instance per domain gateway
- Thread-safe implementation for concurrent access
- See: EE/src/gateway/gateway.py (GatewayRegistry)

### Related Patterns
- **Dependency Injection** (LESS-GEN-01): Alternative to singleton
- **Factory Pattern** (LESS-GEN-02): Creates objects including singletons
- **Registry Pattern**: General case of singleton registry

### Related Lessons
- **LESS-ARCH-02**: Domain Gateway Design
- **LESS-CONC-01**: Thread Safety Patterns

### Related Decisions
- **DEC-ARCH-01**: Universal Gateway Architecture

## Examples by Language

### Java
Double-check locking with volatile keyword. Or use enum singleton (simplest, thread-safe by language spec).

### C#
Static readonly field with lazy initialization or Lazy<T> for thread-safe lazy loading.

### Python
Module-level instance with threading.Lock for thread safety, or use metaclass for singleton pattern.

### Go
sync.Once for guaranteed single initialization, or package-level variables with sync.RWMutex.

### C++
Static local variables with magic static initialization (thread-safe in C++11+), or double-check locking with atomic.

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" - Singleton pattern
- "Effective Java" by Joshua Bloch - Singleton chapter
- Java Memory Model specification
- C++11 memory model and threading guarantees
- Python threading module documentation

## Revision History

- 2025-12-31: Initial creation from EE codebase analysis
