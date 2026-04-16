#!/usr/bin/env python3
"""lee_ligs/demo_simple.py - Simple LIGS Demonstration
Version: 1.0.0
Date: 2026-03-05
Description: Simple demonstration of LIGS functionality

Run with: python lee_ligs/demo_simple.py
"""

import os
import sys
import time

# Add LEE to path to ensure we import LEE's gateway, not UGA's
lee_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if lee_path not in sys.path:
    sys.path.insert(0, lee_path)

from lee.gateway.gateway_core import execute_operation  # noqa: E402
from lee.gateway.gateway_enums import GatewayInterface  # noqa: E402


def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():  # pylint: disable=too-many-statements
    """Run demonstration."""
    print("\n" + "="*60)
    print("  LIGS (Lazy Import Gateway System) Demonstration")
    print("  Version: 1.0.0")
    print("="*60)

    # Demo 1: Basic Usage
    print_section("Demo 1: Basic LIGS Usage")

    # Clear registry
    execute_operation(GatewayInterface.LAZY_IMPORT, "clear")

    # Register modules
    print("\n1. Registering modules...")
    execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "register",
        name="json",
        module_path="json",
        factory=lambda: __import__("json"),
    )

    execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "register",
        name="os",
        module_path="os",
        factory=lambda: __import__("os"),
    )

    print("   [OK] Registered: json, os")

    # Check registered modules
    print("\n2. Checking registered modules...")
    registered = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_all_registered",
    )
    print(f"   Registered: {', '.join(sorted(registered))}")

    # Check loaded modules (should be empty)
    print("\n3. Checking loaded modules (before access)...")
    loaded = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_all_loaded",
    )
    print(f"   Loaded: {', '.join(sorted(loaded)) if loaded else '(none)'}")

    # Access module (triggers load)
    print("\n4. Accessing 'json' module (triggers load)...")
    start = time.perf_counter()
    json_module = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get",
        name="json",
    )
    load_time = (time.perf_counter() - start) * 1000
    print(f"   [OK] Loaded in {load_time:.2f}ms")
    print(f"   [OK] Module: {json_module.__name__}")

    # Check loaded modules (should have json)
    print("\n5. Checking loaded modules (after access)...")
    loaded = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_all_loaded",
    )
    print(f"   Loaded: {', '.join(sorted(loaded))}")

    # Get load time
    print("\n6. Getting load time for 'json'...")
    json_load_time = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_load_time",
        name="json",
    )
    print(f"   Load time: {json_load_time:.2f}ms")

    # Demo 2: Statistics
    print_section("Demo 2: Registry Statistics")

    # Clear and register modules
    execute_operation(GatewayInterface.LAZY_IMPORT, "clear")

    modules = ["json", "os", "sys"]
    for module in modules:
        execute_operation(
            GatewayInterface.LAZY_IMPORT,
            "register",
            name=module,
            module_path=module,
            factory=lambda m=module: __import__(m),
        )

    # Load some modules
    print("\n1. Loading 'json' and 'os'...")
    execute_operation(GatewayInterface.LAZY_IMPORT, "get", name="json")
    execute_operation(GatewayInterface.LAZY_IMPORT, "get", name="os")

    # Get statistics
    print("\n2. Getting registry statistics...")
    stats = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_stats",
    )

    print(f"\n   Total Registered: {stats['total_registered']}")
    print(f"   Total Loaded: {stats['total_loaded']}")
    print(f"   Loaded Names: {', '.join(sorted(stats['loaded_names']))}")

    print("\n   Load Times:")
    for name, load_time in sorted(stats["load_times_ms"].items()):
        print(f"   - {name}: {load_time:.2f}ms")

    # Summary
    print_section("Summary")
    print("\n[SUCCESS] All demonstrations completed!")
    print("\nKey Features Demonstrated:")
    print("  1. Modules load only when first accessed (lazy loading)")
    print("  2. Subsequent accesses return cached modules (fast path)")
    print("  3. Statistics provide visibility into load times")
    print("  4. Full gateway integration via SUGA-ISP pattern")

    print("\nFor more information:")
    print("  - lee_ligs/USAGE_GUIDE.md")
    print("  - lee_ligs/IMPLEMENTATION_SUMMARY.md")
    print("  - tests/test_ligs_basic.py")


if __name__ == "__main__":
    main()
