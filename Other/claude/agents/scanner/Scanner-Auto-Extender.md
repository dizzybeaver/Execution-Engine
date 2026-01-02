# Scanner Auto‑Extender for EE 2.1 Compliance

This document defines how the compliance scanner MUST automatically extend itself
whenever:

- The Enforcer Agent reports a violation
- The Coder Agent introduces a regression
- The CI pipeline detects a new pattern
- A build fails due to a compliance issue
- A human identifies a new anti-pattern

The goal is to ensure the scanner becomes:
- stricter over time
- more complete
- more deterministic
- more aligned with EE 2.1, UG‑ISP, AP‑28, and SIMA

---

# 1. Auto‑Extension Workflow

Whenever a violation is detected, the system MUST follow this workflow:

1. **Capture the violation**
   - Category (gateway, interface, factory, AP‑28, UG‑ISP, SIMA, etc.)
   - File path
   - Line number (if available)
   - Description
   - Expected pattern

2. **Convert the violation into a scanner rule**
   - Regex or AST pattern
   - Severity level
   - Explanation
   - Suggested fix

3. **Insert the rule into the scanner**
   - Append to the appropriate rule set
   - Ensure no duplicates
   - Ensure rule is deterministic
   - Ensure rule does not conflict with existing rules

4. **Re-run the scanner**
   - Validate that the new rule works
   - Ensure no false positives
   - Ensure no false negatives

5. **Commit the updated scanner**
   - The scanner MUST be versioned
   - The scanner MUST be treated as authoritative

---

# 2. Rule Categories

The scanner MUST support the following rule categories:

## 2.1 Gateway Rules
- Legacy constructors
- Missing get_config
- Missing DI injection
- Missing pooling
- Missing factory delegation
- Cross-domain imports
- Missing call_operation
- Legacy execute()
- Legacy error classes

## 2.2 Interface Rules
- Logic inside interfaces
- Missing DI
- Missing factory delegation
- Cross-domain imports
- Missing type isolation

## 2.3 Factory Rules
- Logic inside factories
- Missing execution-only behavior
- Missing pooling
- Missing DI
- Cross-domain imports
- Wrapper creep

## 2.4 Domain Rules
- Partial upgrades
- Hybrid legacy/new patterns
- Missing gateway constructors
- Missing domain registry injection
- Global state
- Legacy patterns

## 2.5 AP‑28 Rules
- Relative imports
- sys.path hacks
- Missing full-path imports
- Missing Lambda-safe import patterns

## 2.6 UG‑ISP Rules
- Cross-domain imports
- Wrapper bypass
- Direct calls instead of call_operation
- Missing DI
- Missing pooling
- Missing isolation
- Missing factory delegation

## 2.7 SIMA Rules
- Outdated knowledge
- Missing updates
- Incorrect categorization
- Missing anti-patterns
- Missing decisions
- Missing workflows
- Missing indexes

---

# 3. Rule Format

Each rule MUST follow this structure:

```json
{
  "id": "RULE-XXXX",
  "category": "gateway|interface|factory|domain|ap28|ugisp|sima",
  "pattern": "regex or AST pattern",
  "severity": "CRITICAL|MAJOR|MINOR",
  "description": "Human-readable explanation",
  "expected": "Expected EE 2.1 / UG-ISP / AP-28 pattern",
  "example_bad": "Code snippet showing violation",
  "example_good": "Code snippet showing correct pattern"
}
