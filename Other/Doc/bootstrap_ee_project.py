```python
#!/usr/bin/env python3
"""
EE Project Bootstrap Script (UG 2.1+)
Creates a fully structured Execution Engine repository with:
- UniversalGatewayFactory
- DomainGatewayFactory
- DomainRegistry
- DI roots
- Pooled gateways, interfaces, factories
- SIMA knowledge structure
- Multi-agent governance system
"""

import os
from pathlib import Path
from textwrap import dedent


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str):
    if not path.exists():
        path.write_text(dedent(content), encoding="utf-8")


def bootstrap(root: Path):
    print(f"Bootstrapping EE project at: {root}")

    # ----------------------------------------------------------------------
    # EE/ — Execution Engine
    # ----------------------------------------------------------------------
    ee = root / "EE"
    ensure_dir(ee)

    # Public entry point
    write(ee / "__init__.py", """
from .universal_gateway.gateway_factory import UniversalGatewayFactory

_ug_factory = UniversalGatewayFactory()
_ug_pool = []

def _get_ug():
    if _ug_pool:
        return _ug_pool.pop()
    return _ug_factory.build_gateway()

def _return_ug(ug):
    _ug_pool.append(ug)

def execute_operation(domain, interface, operation, **kwargs):
    ug = _get_ug()
    try:
        return ug.execute_operation(domain, interface, operation, **kwargs)
    finally:
        _return_ug(ug)
""")

    # ----------------------------------------------------------------------
    # Universal Gateway Core
    # ----------------------------------------------------------------------
    ug = ee / "universal_gateway"
    ensure_dir(ug)

    write(ug / "gateway.py", "# UniversalGateway implementation (DI + pooled)")
    write(ug / "gateway_factory.py", "# UniversalGatewayFactory implementation")
    write(ug / "domain_gateway_factory.py", "# DomainGatewayFactory implementation")
    write(ug / "gateway_registry.py", "# DomainRegistry implementation")
    write(ug / "__init__.py", "")

    # ----------------------------------------------------------------------
    # Domains (skeleton only)
    # ----------------------------------------------------------------------
    domains = [
        "foundation", "observability", "security", "operations", "networking",
        "scanner", "test", "infrastructure", "cli", "doc", "sdk",
        "web", "dashboard", "ha", "isp"
    ]

    for domain in domains:
        d = ee / domain
        ensure_dir(d)
        write(d / "gateway.py", f"# {domain.capitalize()}Gateway implementation")
        write(d / "__init__.py", f"# {domain.capitalize()} domain package")

    # ----------------------------------------------------------------------
    # SIMA Knowledge System
    # ----------------------------------------------------------------------
    sima = root / "SIMA" / "projects" / "EE" / "architecture"
    ensure_dir(sima)

    write(sima / "EE-Universal-Gateway-Architecture.md", "# Architecture doc placeholder")
    write(sima / "EE-Universal-Gateway-Implementation-Guide.md", "# Implementation guide placeholder")
    write(sima / "EE-Multi-Agent-Workflow.md", "# Multi-agent workflow placeholder")
    write(sima / "EE-UG-Rules-For-AI-Agents.md", "# UG rules placeholder")
    write(sima / "EE-Domain-Interface-Catalog.md", "# Domain/interface catalog placeholder")

    # ----------------------------------------------------------------------
    # Agents
    # ----------------------------------------------------------------------
    agents = root / "agents"
    ensure_dir(agents)

    for sub in ["coordinator", "enforcers", "coders"]:
        ensure_dir(agents / sub)

    write(agents / "coordinator" / "coordinator_agent.md", "# Coordinator agent spec")
    write(agents / "enforcers" / "architecture_compliance_enforcer.md", "# Enforcer agent spec")
    write(agents / "coders" / "python_ug_compliant_coder.md", "# Coder agent spec")

    # ----------------------------------------------------------------------
    # Scripts
    # ----------------------------------------------------------------------
    scripts = root / "scripts"
    ensure_dir(scripts)

    write(scripts / "bootstrap_ee_project.py", "# This script (self)")
    write(scripts / "validate_ee_repo.py", "# UG-ISP validation script placeholder")
    write(scripts / "run_coordinator.py", "# Coordinator runner placeholder")
    write(scripts / "run_enforcer.py", "# Enforcer runner placeholder")
    write(scripts / "run_coder.py", "# Coder runner placeholder")

    print("EE project bootstrap complete.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: bootstrap_ee_project.py <project_root>")
        exit(1)

    root = Path(sys.argv[1]).resolve()
    ensure_dir(root)
    bootstrap(root)
