# LESS-GEN-01: Dependency Injection Pattern

**Status**: Active
**Category**: Architecture
**Source**: EE Codebase Analysis
**Created**: 2025-12-31

## Summary

Inject dependencies from external sources rather than creating them internally through imports or direct instantiation. This enables loose coupling between components and improves testability.

## The Principle

### What is Dependency Injection?

Dependency Injection (DI) is a technique where a component receives its dependencies from external sources rather than creating them itself. The component declares what it needs, and something else provides it.

### Core Concept

**Without DI**:
- Component creates its own dependencies
- Component knows how to find and instantiate dependencies
- Tight coupling between component and dependency
- Difficult to substitute implementations

**With DI**:
- Component declares required dependencies
- External source provides dependencies
- Loose coupling - component depends on abstractions
- Easy to substitute implementations for testing or different contexts

## Benefits

### 1. Testability
- Substitute real dependencies with test doubles (mocks, stubs, fakes)
- Isolate units under test
- Control test scenarios precisely
- Faster test execution

### 2. Loose Coupling
- Components depend on abstractions, not concrete implementations
- Swap implementations without changing consuming code
- Reduce ripple effects of changes
- Enable independent evolution of components

### 3. Flexibility
- Configure different implementations for different environments
- Enable feature toggles and A/B testing
- Support runtime behavior changes
- Facilitate plugin architectures

### 4. Maintainability
- Explicit dependencies are visible at interface level
- Clear data flow through the system
- Easier to understand component relationships
- Simpler refactoring

## Types of Dependency Injection

### Constructor Injection
Dependencies provided during component initialization. Best for required dependencies that cannot change during the component lifecycle.

### Setter/Property Injection
Dependencies provided via setter methods or properties after initialization. Best for optional dependencies or those that may change.

### Interface Injection
Dependencies provided through an interface specifically for injection. Less common but useful in certain frameworks.

### Parameter Injection
Dependencies provided with each method call. Best for dependencies that vary per operation.

## When to Use

### Ideal Situations
- Building maintainable, testable systems
- Implementing plugin architectures
- Creating reusable components
- Following SOLID principles
- Developing with automated testing

### When to Avoid
- Very simple scripts with no testing requirements
- Pure functions that should remain stateless
- Performance-critical code paths where DI overhead is measurable
- Situations where DI framework complexity exceeds project needs

## Best Practices

### Design for DI
- Design components with explicit dependencies
- Depend on abstractions (interfaces, protocols) not concretions
- Make dependencies clear and minimal
- Avoid hidden dependencies (global state, singletons accessed directly)

### Organize Dependencies
- Use composition over inheritance
- Keep dependency graphs shallow
- Avoid circular dependencies
- Group related functionality to reduce dependency count

### Lifecycle Management
- Match dependency lifecycles to component needs
- Use scopes appropriately (transient, request, singleton)
- Consider thread safety for shared dependencies
- Plan for resource cleanup

## Common Pitfalls

### Over-Injection
- Too many dependencies indicate component does too much
- Consider splitting large components
- Look for opportunities to group related dependencies

### Service Location Anti-Pattern
- Using a service locator to "cheat" DI
- Defeats the purpose of explicit dependencies
- Creates hidden dependencies again
- Reduces testability benefits

### Tight Coupling to DI Framework
- Avoid framework-specific annotations throughout business logic
- Keep DI configuration separate from business code
- Consider framework-agnostic patterns where possible

## Cross-References

### Python/EE Implementation
- See EE codebase gateway for constructor injection example
- Domain interfaces receive gateway registry via initialization
- Factories injected into interfaces for execution units

### Related Patterns
- **Factory Pattern** (DEC-GEN-01): Often used with DI to create dependencies
- **Singleton Registry** (DEC-GEN-02): DI provides alternative to global state
- **Inversion of Control Container**: Framework that automates DI

### Related Lessons
- **LESS-GEN-02**: Factory Pattern for Execution Units
- **LESS-ARCH-01**: Interface Isolation Principle

## Examples by Language

### Java/Spring
Framework provides automatic constructor injection. Dependencies declared as constructor parameters.

### C#/.NET
Built-in DI container in ASP.NET Core supports constructor injection by default.

### Python
Manual injection through constructors, common in DI frameworks like dependency_injector.

### JavaScript/TypeScript
Popular DI frameworks include InversifyJS, Awilix, and TypeScript-RxJS.

### Go
Often uses functional options pattern or explicit constructor functions.

## References

- Martin Fowler's article on Inversion of Control Containers and Dependency Injection
- "Clean Architecture" by Robert C. Martin
- SOLID principles, specifically Dependency Inversion Principle
- Google Guice documentation for Java
- Microsoft's DI documentation for .NET

## Revision History

- 2025-12-31: Initial creation from EE codebase analysis
