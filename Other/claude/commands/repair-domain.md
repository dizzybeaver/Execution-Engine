---
description: Repairs a specific EE domain using strict repair cycle rules
arguments:
  - name: domain
    description: The EE domain to repair (e.g., authentication, authorization, gateway)
    required: true
---

You are running the strict repair cycle on a specific EE domain: {{domain}}

Follow the strict repair cycle process:
1. ENFORCE SCAN: Enforcer agent scans the {{domain}} domain for violations
2. CODER REPAIR: Coder agent fixes all identified violations
3. ENFORCE VALIDATE: Enforcer agent validates all repairs
4. CONVERGENCE LOOP: Repeat steps 2-3 until PASS is achieved

Repair scope for {{domain}} domain:
- All interface files
- All factory implementations
- All domain gateways
- All tests and specifications

Domain-specific checks:
- UG (Universal Gateway) architecture compliance
- Interface isolation (no imports outside package)
- Factories as concrete execution units
- Proper route handling through UG

Continue the convergence loop until:
- Enforcer returns PASS for {{domain}} domain
- All red flags cleared
- All SIMA standards met
- All EE architecture rules satisfied

Report final status with convergence count for {{domain}}.
