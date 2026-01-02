---
description: Validates EE 2.1, UG-ISP, and AP-28 architecture rules
---

You are performing EE architecture validation against EE 2.1, UG-ISP, and AP-28 standards.

Validate architecture compliance:

1. UNIVERSAL GATEWAY (UG) RULES:
   - UG is the ONLY entry point for cross-component execution
   - All external calls go through UG.execute_operation(route, payload)
   - No components bypass UG

2. INTERFACE ISOLATION:
   - Interfaces must not import outside their package
   - Interfaces define contracts only
   - No implementation in interfaces

3. FACTORY RULES:
   - Factories are the concrete execution units
   - Factories implement interfaces
   - Execution flow: External Code → UG → Domain Gateway → Interface → Factory

4. DOMAIN GATEWAYS:
   - Each domain has a gateway
   - Gateway routes to appropriate interfaces
   - Gateway validates domain-specific rules

5. EE 2.1 COMPLIANCE:
   - No legacy patterns
   - Modern error handling
   - Proper typing
   - Clean separation of concerns

6. AP-28 PATTERNS:
   - Authorization patterns followed
   - Security measures in place
   - Proper session handling

Return PASS or FAIL with:
- Architecture violations
- Components bypassing UG
- Interface isolation breaches
- Factory pattern issues
- Specific files and line numbers
