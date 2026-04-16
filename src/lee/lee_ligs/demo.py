#!/usr/bin/env python3
"""lee_ligs/demo.py - LIGS Demonstration Script
Version: 1.0.0
Date: 2026-03-05
Description: Demonstrates LIGS functionality

Run with: python lee_ligs/demo.py
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

# Cache environment variable at module load time
# For AWS Lambda: Read from environment variable set by Lambda configuration
# For local testing: .env file should set this via environment variable
_HA_ENABLED = os.getenv("HOME_ASSISTANT_ENABLE", "false").lower() == "true"


def print_section(title: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demo_basic_usage():
    """Demonstrate basic LIGS usage."""
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

    print("   ✓ Registered: json, os")

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
    print(f"   ✓ Loaded in {load_time:.2f}ms")
    print(f"   ✓ Module: {json_module.__name__}")

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


def demo_preload():
    """Demonstrate preload functionality."""
    print_section("Demo 2: Preload Functionality")

    # Clear registry
    execute_operation(GatewayInterface.LAZY_IMPORT, "clear")

    # Register multiple modules
    print("\n1. Registering modules...")
    modules = ["json", "os", "sys", "time"]
    for module in modules:
        execute_operation(
            GatewayInterface.LAZY_IMPORT,
            "register",
            name=module,
            module_path=module,
            factory=lambda m=module: __import__(m),
        )
    print(f"   ✓ Registered: {', '.join(modules)}")

    # Preload specific modules
    print("\n2. Preloading 'json' and 'os'...")
    execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "preload",
        names=["json", "os"],
    )

    # Check loaded modules
    print("\n3. Checking loaded modules...")
    loaded = execute_operation(
        GatewayInterface.LAZY_IMPORT,
        "get_all_loaded",
    )
    print(f"   Loaded: {', '.join(sorted(loaded))}")
    print("   Expected: json, os (not sys, time)")


def demo_statistics():
    """Demonstrate statistics functionality."""
    print_section("Demo 3: Registry Statistics")

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


def demo_ha_suga():
    """Demonstrate HA-SUGA integration."""
    print_section("Demo 4: HA-SUGA Integration")


    # Check if HA enabled (cached at module level)
    # For AWS Lambda: Read from environment variable set by Lambda configuration
    # For local testing: .env file should set this via environment variable
    if not _HA_ENABLED:
        print("\n⚠ HOME_ASSISTANT_ENABLE not set")
        print("  Set HOME_ASSISTANT_ENABLE=true to test HA-SUGA integration")
        print("  Skipping this demo...")
        return

    try:
        from lee.home_assistant import HA_ENABLED, get_ha_module  # noqa: E402, pylint: disable=import-outside-toplevel

        print("\n1. HA-SUGA Status:")
        print(f"   HA_ENABLED: {HA_ENABLED}")

        print("\n2. Trying to load HA modules...")
        print("   Note: This will fail if HA modules don't exist,")
        print("   but demonstrates the lazy loading mechanism.")

        try:
            # Try to load ha_gateway
            print("\n   Loading ha_gateway...")
            get_ha_module("ha_gateway")
            print("   ✓ ha_gateway loaded successfully")
        except ImportError as e:
            print(f"   ✗ ha_gateway not found: {e}")
            print("   This is expected if HA modules don't exist")

    except ImportError as e:
        print(f"\n⚠ home_assistant package not available: {e}")
        print("  This is expected in non-HA environments")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("  LIGS (Lazy Import Gateway System) Demonstration")
    print("  Version: 1.0.0")
    print("  Date: 2026-03-05")
    print("="*60)

    try:
        # Run demos
        demo_basic_usage()
        demo_preload()
        demo_statistics()
        demo_ha_suga()

        # Final summary
        print_section("Summary")
        print("\n✅ All demonstrations completed successfully!")
        print("\nKey Takeaways:")
        print("  1. Modules load only when first accessed (lazy loading)")
        print("  2. Subsequent accesses return cached modules (fast path)")
        print("  3. Preload allows warming up critical modules")
        print("  4. Statistics provide visibility into load times")
        print("  5. HA-SUGA integration enables lazy loading for HA modules")

        print("\nFor more information, see:")
        print("  - lee_ligs/USAGE_GUIDE.md")
        print("  - lee_ligs/IMPLEMENTATION_SUMMARY.md")

    except RuntimeError as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback  # noqa: E402
        traceback.print_exc()


if __name__ == "__main__":
    main()
