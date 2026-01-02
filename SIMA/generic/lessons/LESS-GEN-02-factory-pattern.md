# LESS-GEN-02: Factory Pattern for Execution Units

**Status**: Active
**Category**: Design Pattern
**Source**: EE Codebase Analysis
**Created**: 2025-12-31

## Summary

Use factory objects to encapsulate the creation, configuration, and lifecycle management of execution units (components that perform work). Factories separate the "what" from the "how" of object creation.

## The Principle

### What is a Factory?

A factory is a component responsible for creating and configuring other components. It encapsulates the knowledge of how to construct objects properly, hiding this complexity from clients.

### Core Concept

**Without Factory**:
- Clients know exactly how to create objects
- Construction logic scattered throughout codebase
- Difficult to change construction process
- Tight coupling to specific implementations

**With Factory**:
- Clients request objects from factory
- Construction logic centralized in factory
- Easy to change construction process
- Clients depend on abstraction, not construction details

## Benefits

### 1. Resource Management
- Control object lifecycle from creation to destruction
- Manage connection pools, caches, and other resources
- Implement object pooling and reuse strategies
- Ensure proper cleanup and resource release

### 2. Encapsulation of Complexity
- Hide complex construction logic behind simple interface
- Manage dependencies and configuration details
- Handle conditional instantiation logic
- Simplify client code significantly

### 3. Consistency
- Ensure all objects are created correctly
- Enforce initialization invariants
- Apply consistent configuration
- Prevent invalid object states

### 4. Flexibility
- Change implementation details without affecting clients
- Switch between different concrete types
- Enable dynamic configuration based on environment
- Support feature flags and runtime behavior changes

### 5. Testability
- Substitute factory in tests to provide test doubles
- Create objects with specific test configurations
- Isolate construction logic for unit testing
- Control object creation in integration tests

## Factory Types

### Simple Factory
Single method with parameter(s) determining which object type to create. Most basic form, useful for limited type variations.

### Factory Method
Interface defines creation method, subclasses implement it. Allows polymorphic object creation. Useful when object creation logic varies by context.

### Abstract Factory
Interface for creating families of related objects. Ensures compatibility between created objects. Useful for platform-specific implementations.

### Builder Factory
Creates complex objects step-by-step before returning them. Handles objects requiring extensive configuration. Useful for objects with many optional parameters.

## When to Use

### Ideal Situations
- Creating objects with complex initialization logic
- Managing object lifecycle and resources
- Encapsulating object creation behind interface
- Supporting multiple implementations or configurations
- Coordinating creation of related objects

### When to Avoid
- Simple objects with no configuration (e.g., data transfer objects)
- When construction logic is trivial and unlikely to change
- When object type is known at compile time and never varies
- Performance-critical paths where factory overhead is measurable

## Best Practices

### Design Principles
- **Single Responsibility**: Each factory creates one type or family of related objects
- **Interface Segregation**: Provide focused factory interfaces, not generic ones
- **Dependency Inversion**: Depend on abstractions, not concrete factory implementations
- **Clear Naming**: Make factory purpose obvious from name (e.g., DatabaseConnectionFactory)

### Implementation Guidelines
- Return interfaces or abstract types, not concrete classes
- Make factory stateless if possible (thread-safe, reusable)
- Validate inputs and fail fast for invalid requests
- Document preconditions, postconditions, and invariants
- Consider factory lifecycle (singleton vs. per-use)

### Error Handling
- Provide clear error messages for creation failures
- Include context about what failed and why
- Consider custom exception types for factory errors
- Handle resource cleanup when creation partially fails

### Configuration Management
- Externalize configuration when possible
- Support environment-specific settings
- Validate configuration at factory initialization
- Provide sensible defaults while allowing customization

## Factory vs. Dependency Injection

### Complementary Patterns
Factories and DI work well together:
- DI container uses factories to create objects
- Factories can be injected into clients
- Factories handle complex creation, DI handles wiring

### When to Use Each
- **Factory**: Complex creation logic, lifecycle management, multiple related objects
- **DI**: Simple object creation, managing dependencies between components
- **Together**: DI injects factory, factory creates complex objects on demand

## Common Pitfalls

### God Factory
- Factory that creates too many different types
- Violates single responsibility principle
- Becomes maintenance bottleneck
- **Solution**: Split into focused factories

### Hidden Dependencies
- Factory creates objects but doesn't expose their dependencies
- Clients don't know what dependencies created objects require
- Leads to runtime failures
- **Solution**: Make dependencies explicit through factory interface or created objects

### Mutable State in Factories
- Factory holds state that changes between calls
- Can cause thread safety issues
- Makes object creation non-deterministic
- **Solution**: Keep factories stateless or clearly document thread safety

### Overly Complex Factories
- Too many configuration options
- Difficult to understand and use correctly
- **Solution**: Provide sensible defaults, use builder pattern for complex cases

## Factory Lifecycle

### Singleton Factories
- Single instance used throughout application
- Must be thread-safe
- Appropriate for stateless factories or those managing global resources

### Scoped Factories
- Instance exists for specific scope (request, session, transaction)
- Useful for context-specific object creation
- Must manage scope lifecycle correctly

### Transient Factories
- New instance created each time
- Appropriate for stateful, short-lived factories
- No thread safety concerns

## Testing with Factories

### Unit Testing
- Mock factories to provide test doubles
- Verify correct factory methods called
- Test error handling with failing factories

### Integration Testing
- Use real factories with test configuration
- Verify objects created with correct settings
- Test resource cleanup and lifecycle

### Test Factories
- Create specialized factories for testing
- Provide pre-configured test objects
- Reduce test setup code duplication

## Cross-References

### Python/EE Implementation
- EE codebase factories in each domain interface
- Factories create gateway clients, connectors, processors
- Gateway registry manages factory lifecycle
- See: EE/src/*/interface/*_factory.py

### Related Patterns
- **Dependency Injection** (LESS-GEN-01): Often used together
- **Singleton Registry** (DEC-GEN-02): Factories can manage singletons
- **Builder Pattern**: For complex object construction
- **Abstract Factory**: For families of related objects

### Related Decisions
- **DEC-ARCH-01**: Universal Gateway Architecture
- **DEC-ARCH-02**: Domain Gateway Design

## Examples by Language

### Java
Abstract Factory interface with concrete implementations for different object types.

### C#
Factory classes with static Create methods or instance methods for dependency injection.

### Python
Functions or classes with create methods, often using __call__ for natural syntax.

### Go
Functions returning interfaces, often with functional options for configuration.

### JavaScript/TypeScript
Classes or functions with create methods, supporting both sync and async creation.

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" - Gang of Four
- "Refactoring to Patterns" by Joshua Kerievsky
- Martin Fowler's articles on factory patterns
- "Clean Code" by Robert C. Martin

## Revision History

- 2025-12-31: Initial creation from EE codebase analysis
