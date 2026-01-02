# LESS-GEN-04: Exception Chaining

**Status**: Active
**Category**: Error Handling
**Source**: EE Codebase Analysis
**Created**: 2025-12-31

## Summary

When catching and re-raising exceptions, preserve the original exception as the root cause. Exception chaining maintains complete error context, enabling faster debugging and more accurate error resolution.

## The Principle

### What is Exception Chaining?

Exception chaining is the practice of wrapping a lower-level exception in a higher-level exception while maintaining a reference to the original. This creates a chain of exceptions from the root cause to the final error.

### Core Concept

**Without Chaining**:
- Lower-level exception is lost
- Only high-level context visible
- Root cause obscured or missing
- Difficult to debug and diagnose

**With Chaining**:
- Original exception preserved
- Full stack trace available
- Root cause clear
- Each layer adds appropriate context

### Why It Matters

When an error propagates through multiple layers of abstraction, each layer should:
1. Catch exceptions from lower layers
2. Add context relevant to that layer's abstraction
3. Re-raise a new exception with the original attached
4. Preserve the complete causal chain

## Benefits

### 1. Complete Stack Trace
- See the full call chain from root cause to final error
- Every layer's contribution visible
- No missing information
- Complete picture of failure

### 2. Root Cause Visibility
- Original error never lost
- See exactly what started the chain
- No need to guess or infer
- Accurate diagnosis possible

### 3. Layered Context
- Each abstraction layer adds its context
- High-level business meaning preserved
- Low-level technical details available
- Both perspectives visible

### 4. Faster Debugging
- Immediate understanding of failure
- No need for extensive logging
- Fewer reproduction attempts
- Direct path to solution

### 5. Better Error Messages
- High-level exception describes what failed
- Low-level exception explains why
- Combined message is comprehensive
- User gets meaningful information

## When to Use

### Always Chain When:
- Catching and re-raising with additional context
- Translating low-level exceptions to domain-specific types
- Wrapping third-party library exceptions
- Crossing abstraction boundaries
- Adding business logic context to technical failures

### May Not Need Chaining When:
- Simply re-raising without adding context (just use "raise")
- Creating brand new errors unrelated to caught exception
- Implementing retry logic where original is handled
- In top-level handlers that log and terminate

## Best Practices

### What to Include in Chain

**At Each Layer**:
- What operation was being performed
- What inputs or state were involved
- Why this failure matters at this layer
- Any relevant identifiers (IDs, names, paths)

**Example Chain**:
1. Database: Connection timeout
2. Data layer: Failed to fetch user record
3. Business layer: Unable to authenticate user
4. API layer: Login request failed

Each adds context while preserving root cause.

### Choosing What to Chain

**Chain Exception When**:
- Current error directly caused by caught exception
- Caught exception is essential context
- Caller needs to see root cause
- Part of same failure scenario

**Don't Chain When**:
- Unrelated new error occurs
- Original exception fully handled
- Starting new operation after recovery
- Creating error for notification/logging only

### Message Construction

**Higher-Level Message**:
- Focus on what failed at this abstraction level
- Use domain language, not technical details
- Add context relevant to caller
- Make sense without seeing chained exception

**Lower-Level Exception**:
- Original message preserved unchanged
- Contains technical details
- Shows exact failure point
- Provides raw diagnostic data

### Exception Type Selection

**Appropriate Types**:
- Create domain-specific exception types
- Use existing types when they fit
- Consider exception hierarchy
- Make types meaningful to callers

**Type Granularity**:
- One type per error category
- Not too broad (catch-all types)
- Not too narrow (one type per message)
- Balance between specificity and simplicity

## Language-Specific Patterns

### Python
Use "raise ... from ..." syntax for explicit chaining. Use "raise" without "from" for implicit chaining. Access chained exception via __cause__ attribute.

### Java
Use constructor that accepts cause parameter: "new Exception(message, cause)". Access via getCause(). All standard exceptions support chaining.

### C#
Use constructor that accepts innerException: "new Exception(message, innerException)". Access via InnerException property.

### JavaScript/Node.js
Custom Error classes with cause property. Standard Error objects don't traditionally support chaining (though modern JS is adding support).

### Go
Create custom error types that wrap original error. Use fmt.Errorf with %w verb to wrap errors. Use errors.Unwrap() to access wrapped error.

### C++
Use nested try-catch blocks or std::exception_ptr. Standard exceptions don't have built-in chaining, but custom types can support it.

## Common Patterns

### Layer Translation
Low-level technical exception becomes high-level domain exception.

Example:
- Network timeout → Service unavailable
- SQL constraint violation → Duplicate entity
- File not found → Configuration missing

### Context Addition
Add business context to technical failure.

Example:
- Database error → Failed to save order #12345
- Cache miss → Unable to load user preferences for user@domain.com
- Validation error → Invalid payment method for subscription

### Abstraction Boundary Crossing
Translate between layers with appropriate abstractions.

Example:
- Database layer → Repository layer → Service layer → API layer
- Each layer uses exception types appropriate to its abstraction

## Common Pitfalls

### Breaking the Chain
- Catching exception and throwing new without linking
- Using exception message only, discarding exception object
- Logging and then throwing new exception
- **Solution**: Always preserve original exception

### Over-Chaining
- Chaining exceptions that aren't related
- Creating chains that are too long (>5 levels)
- Chaining for every single layer
- **Solution**: Only chain when adding meaningful context

### Lost Context
- Not adding context at abstraction boundaries
- Generic exception types at high level
- Messages that don't explain the failure
- **Solution**: Add layer-specific context with each translation

### Misleading Chains
- Chaining exceptions where cause relationship is unclear
- Using same exception type at all levels
- Inconsistent chaining in similar scenarios
- **Solution**: Chain only when causal relationship is clear

### Information Overload
- Exposing low-level details to end users
- Including sensitive data in exception chains
- Very long stack traces that obscure root cause
- **Solution**: Tailor exception display to audience

## Testing Considerations

### Unit Testing
- Test exception chains are preserved correctly
- Verify root cause is accessible
- Check messages at each level
- Test exception type hierarchies

### Integration Testing
- Verify exceptions propagate across boundaries
- Test chains through multiple layers
- Ensure logging captures full chain
- Validate monitoring/alerting on root cause

### Error Handling Testing
- Test that chained exceptions are handled correctly
- Verify cleanup happens despite chained exceptions
- Test retry logic with chained exceptions
- Ensure monitoring tracks root causes

## Logging and Monitoring

### Logging Strategy
- Log full exception chain at error boundaries
- Include all stack traces and messages
- Log at appropriate level for each layer
- Structure logs for searchability

### Monitoring and Metrics
- Track root cause exceptions for metrics
- Alert on critical exceptions in chain
- Analyze patterns in exception chains
- Use traces to follow exception flow

### Observability
- Include trace/request IDs in exceptions
- Correlate exception chains across services
- Link exceptions to logs and metrics
- Maintain chain across distributed systems

## Cross-References

### Python/EE Implementation
- EE codebase chains exceptions across gateway layers
- Low-level network errors wrapped in domain exceptions
- See: EE/src/*/interface/*_errors.py (exception definitions)

### Related Lessons
- **LESS-GEN-03**: Descriptive Error Messages
- **LESS-GEN-05**: Error Recovery Strategies

### Related Decisions
- **DEC-GEN-02**: Error Handling Strategy

## Examples by Scenario

### Database Operation
1. SQL: Unique constraint violation
2. ORM: Duplicate entity error
3. Repository: Entity already exists
4. Service: Cannot create duplicate user
5. API: 409 Conflict with error details

### File Processing
1. OS: Permission denied
2. File library: Cannot open file
3. Parser: Failed to read configuration
4. Service: Unable to load application settings
5. API: 500 Internal Server Error

### External API Call
1. HTTP: Connection timeout
2. Client: Service unavailable
3. Integration: Payment gateway unreachable
4. Service: Cannot process payment
5. UI: Unable to complete purchase

## Best Practice Checklist

When implementing exception handling:
- [ ] Always preserve caught exception when re-raising
- [ ] Add relevant context at each abstraction layer
- [ ] Use appropriate exception types for each layer
- [ ] Include helpful error messages
- [ ] Test exception chains are preserved
- [ ] Log full chain at error boundaries
- [ ] Consider security (don't expose sensitive data)
- [ ] Make root cause accessible in monitoring
- [ ] Handle chained exceptions appropriately
- [ ] Document exception type hierarchy

## References

- "Effective Java" by Joshua Bloch - Exception handling chapter
- "Clean Code" by Robert C. Martin - Error handling
- Python Exception Chaining documentation (PEP 3134)
- Microsoft .NET Exception handling guidelines
- "Release It!" by Michael Nygard - Exception handling patterns

## Revision History

- 2025-12-31: Initial creation from EE codebase analysis
