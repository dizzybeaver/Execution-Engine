# LESS-GEN-03: Descriptive Error Messages

**Status**: Active
**Category**: Error Handling
**Source**: EE Codebase Analysis
**Created**: 2025-12-31

## Summary

Error messages should provide complete context including what happened, what was expected, what was received, and available options or remedies. Well-crafted error messages enable self-debugging and dramatically reduce development time.

## The Principle

### What Makes a Good Error Message?

A good error message answers the fundamental questions:
1. **What happened?** - Clear description of the error condition
2. **Where did it happen?** - Location in code/system (when relevant)
3. **Why is it a problem?** - Why the operation cannot proceed
4. **What did I expect?** - Valid values, states, or conditions
5. **What did I get instead?** - Actual value, state, or condition
6. **What can I do?** - Suggested remedies or solutions
7. **Where can I learn more?** - Documentation references or examples

### Core Concept

**Poor Error Message**:
- "Invalid input"
- "Error occurred"
- "Operation failed"
- Generic or cryptic codes only

**Good Error Message**:
- "Invalid 'timeout' value: -5. Expected a positive integer (1-3600 seconds)"
- "Failed to connect to database 'prod_db'. Host 'db.example.com' unreachable. Check network connectivity and firewall rules."
- "Missing required field 'user_id' in request payload. See API documentation at /docs/api#create-user"

## Benefits

### 1. Self-Debugging
- Users can identify and fix issues without support
- Reduces time spent on troubleshooting
- Empowers users to solve their own problems
- Creates positive user experience

### 2. Faster Development
- Developers spend less time investigating errors
- Root cause is immediately apparent
- No need for additional debugging sessions
- Accelerates development velocity

### 3. Better User Experience
- Users feel guided, not frustrated
- Clear path to resolution
- Professional and helpful tone
- Builds trust in system quality

### 4. Reduced Support Load
- Fewer support tickets and questions
- Knowledge base built into error messages
- Users become more self-sufficient
- Support team can focus on complex issues

### 5. Easier Maintenance
- Future developers understand code faster
- Error messages serve as inline documentation
- Clearer intent and constraints
- Reduced cognitive load

## Message Components

### Essential Components

**What Happened**:
- Clear description of error condition
- Use active voice and present tense
- Avoid jargon unless user is technical
- Example: "Failed to open file" not "File opening failure"

**What Was Expected**:
- Valid values, types, or ranges
- Required format or structure
- Pre-conditions or dependencies
- Example: "Expected a positive integer between 1 and 100"

**What Was Received**:
- Actual value that caused error
- Type or format received
- Current state or condition
- Example: "Received string value 'abc'"

### Helpful Components (When Relevant)

**Location Context**:
- File name and line number
- Function or method name
- Module or component name
- URL or endpoint

**Remediation Steps**:
- Specific actions to fix
- Configuration changes needed
- Commands to run
- Example: "Run 'npm install' to install missing dependencies"

**References**:
- Documentation links
- Related resources
- Similar working examples
- Support contacts

**Affected Resources**:
- Which components or data affected
- Scope of the problem
- What still works
- Impact assessment

## Writing Guidelines

### Structure and Format

**Be Specific**:
- Include actual values, not generic descriptions
- Show exact validation criteria
- Provide concrete examples
- Use precise terminology

**Be Concise**:
- Every word should add information
- Avoid redundant phrases
- Use formatting for readability (line breaks, bullets)
- Front-load important information

**Be Actionable**:
- Suggest specific fixes when possible
- Prioritize most likely solutions
- Provide step-by-step guidance for complex issues
- Include examples or templates

**Be Consistent**:
- Use consistent terminology across messages
- Follow established style guide
- Maintain consistent tone and format
- Align with project standards

### Tone and Style

**Professional, Not Blaming**:
- Avoid "you" statements that blame user
- Focus on the problem, not the person
- Don't use exclamation points (feels like yelling)
- Example: "Invalid input" not "You entered invalid input"

**Empathetic, Not Emotional**:
- Acknowledge frustration without being emotional
- Avoid overly casual language
- Don't use humor or sarcasm
- Maintain professional distance

**Technical, Not Cryptic**:
- Use appropriate technical terms for audience
- Explain technical concepts when needed
- Avoid internal jargon or acronyms
- Define specialized terms on first use

## Error Message Patterns

### Validation Errors

**Pattern**: "Invalid {field}. Expected {criteria}. Received {actual}."

Example:
- "Invalid 'email'. Expected valid email address. Received 'user@'."
- "Timeout value out of range. Expected 1-3600 seconds. Received -5."
- "Missing required field 'password'. Cannot create user account."

### Configuration Errors

**Pattern**: "{Operation} failed due to {config_issue}. {Resolution}."

Example:
- "Failed to connect to database. Connection string missing 'host' parameter. Add 'host' to configuration file."
- "TLS certificate expired. Update certificate in /etc/ssl/certs/app.crt"

### Resource Errors

**Pattern**: "{Resource} {action} failed. {Reason}. {Resolution}."

Example:
- "File '/data/config.json' not found. Verify file exists and application has read permissions."
- "Database connection pool exhausted. Max connections: 10. Increase pool size or reduce concurrent operations."

### Permission Errors

**Pattern**: "Permission denied for {operation} on {resource}. {Required_permission}. {Resolution}."

Example:
- "Permission denied for DELETE on /api/users. Requires 'admin' role. Contact system administrator for access."
- "Cannot write to file. Directory is read-only. Choose a different location or modify permissions."

## Context-Specific Considerations

### API Error Messages
- Include endpoint name and HTTP method
- Show request ID for tracing
- Reference API documentation
- Provide example payloads

### CLI Error Messages
- Show command that failed
- Display correct syntax
- Suggest similar commands
- Reference help documentation

### GUI Error Messages
- Use user-friendly language
- Avoid technical details (show in "Details" section)
- Provide actionable buttons (Retry, Cancel, Help)
- Don't show stack traces to end users

### Library Error Messages
- Include library and version
- Show calling code location when possible
- Provide integration examples
- Link to API documentation

## Internationalization (i18n)

### Design for Translation
- Use externalized message strings
- Separate message text from code
- Avoid culture-specific references
- Provide context for translators

### Cultural Considerations
- Date/time format varies by locale
- Number formatting differs
- Color and symbol meanings vary
- Avoid idioms and slang

### Technical Translation
- Technical terms often stay in English
- Provide glossaries for translators
- Context keys help with meaning
- Test with actual translations

## Common Pitfalls

### Too Generic
- "Error occurred" provides no value
- "Invalid input" doesn't say what's wrong
- "Operation failed" doesn't explain why
- **Solution**: Always include specifics

### Too Technical
- Exposing stack traces to end users
- Using internal error codes without explanation
- Including implementation details
- **Solution**: Tailor message to audience

### Too Verbose
- Including irrelevant details
- Long explanations bury key information
- Redundant wording
- **Solution**: Be concise, focus on essentials

### Not Actionable
- Stating problem without solution
- Missing next steps
- No guidance or resources
- **Solution**: Always suggest remediation when possible

### Inconsistent
- Different terms for same concept
- Inconsistent format across messages
- Varying levels of detail
- **Solution**: Use templates and style guide

## Cross-References

### Python/EE Implementation
- EE gateway validation errors show field, expected, received
- Configuration errors include path and resolution
- See: EE/src/*/interface/*_errors.py

### Related Lessons
- **LESS-GEN-04**: Exception Chaining
- **LESS-GEN-05**: Error Recovery Strategies

### Related Decisions
- **DEC-GEN-02**: Error Handling Strategy

## Examples by Language

### Python
Use f-strings or format() to include values. Custom exception classes with formatted messages.

### Java
Throw exceptions with descriptive messages. Use parameterized messages from resource bundles for i18n.

### JavaScript
Use template literals for interpolation. Custom Error classes with formatted messages.

### Go
Use fmt.Errorf with formatting. Wrap errors with context while preserving original.

### C#
Use string interpolation ($ interpolation). Custom exception types with rich properties.

## Best Practice Checklist

When writing error messages, ensure:
- [ ] Describes what happened
- [ ] Explains what was expected
- [ ] Shows what was received
- [ ] Provides context (location, operation)
- [ ] Suggests resolution or next steps
- [ ] Uses appropriate technical level for audience
- [ ] Maintains professional, helpful tone
- [ ] Consistent with project style guide
- [ ] Properly formatted for readability
- [ ] Tested with actual scenarios

## References

- "The Art of Readable Code" by Dustin Boswell and Trevor Foucher
- "Clean Code" by Robert C. Martin - Error Handling chapter
- Microsoft Error Message Guidelines
- Google Developer Documentation Style Guide
- Nielsen Norman Group on error messaging

## Revision History

- 2025-12-31: Initial creation from EE codebase analysis
