"""
Test Doc Gateway Integration

This test verifies the Doc Gateway integration with the EE gateway system.
"""

import sys
sys.path.insert(0, 'D:/Code/Project/EE/src')

from EE.universal_gateway.domain_gateway import EEDomainRegistry
from EE.doc import DocGatewayDomain, create_doc_generator


def test_doc_gateway_import():
    """Test that Doc Gateway can be imported."""
    print("Testing Doc Gateway import...")

    from EE.doc import (
        DocGatewayError,
        CommandDocGenerator,
        RouteDocGenerator,
        ServiceDocGenerator,
        SchemaDocGenerator,
        UnifiedDocGenerator,
        create_doc_generator,
        DocGatewayDomain
    )

    print("✓ All Doc Gateway imports successful")
    return True


def test_doc_gateway_domain():
    """Test Doc Gateway Domain creation."""
    print("\nTesting Doc Gateway Domain creation...")

    # Create registry
    registry = EEDomainRegistry.get_instance()

    # Create doc gateway domain
    doc_gateway = DocGatewayDomain(registry=registry)

    # Test list_all
    all_info = doc_gateway.list_all()

    assert "domain" in all_info
    assert all_info["domain"] == "doc"
    assert "operations" in all_info
    assert len(all_info["operations"]) > 0

    print(f"✓ Doc Gateway Domain created successfully")
    print(f"  Domain: {all_info['domain']}")
    print(f"  Operations: {len(all_info['operations'])}")

    return True


def test_doc_gateway_registration():
    """Test Doc Gateway registration with registry."""
    print("\nTesting Doc Gateway registration...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Create and register doc gateway
    doc_gateway = DocGatewayDomain(registry=registry)

    try:
        registry.register("doc", doc_gateway)
        print("✓ Doc Gateway registered successfully")
    except ValueError:
        print("✓ Doc Gateway already registered (expected)")

    # Verify registration
    assert registry.has_domain("doc"), "Doc domain should be registered"

    # Retrieve gateway
    retrieved = registry.get("doc")
    assert isinstance(retrieved, DocGatewayDomain), "Retrieved gateway should be DocGatewayDomain"

    print("✓ Doc Gateway registration verified")

    return True


def test_doc_gateway_routes():
    """Test Doc Gateway routes."""
    print("\nTesting Doc Gateway routes...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Get doc gateway
    try:
        doc_gateway = registry.get("doc")
    except Exception:
        # If not registered, create it
        doc_gateway = DocGatewayDomain(registry=registry)
        registry.register("doc", doc_gateway)

    # Test list_all route
    result = doc_gateway.execute("doc.list_all", {})

    assert result["domain"] == "doc"
    assert len(result["operations"]) > 0

    print(f"✓ Doc Gateway routes operational")
    print(f"  Available operations: {len(result['operations'])}")

    for op in result["operations"][:3]:  # Show first 3
        print(f"    - {op['route']}: {op['description']}")

    return True


def test_unified_generator():
    """Test Unified Documentation Generator."""
    print("\nTesting Unified Documentation Generator...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Create generator
    generator = create_doc_generator(
        gateway_registry=registry,
        output_dir="./test_docs",
        formats=["markdown"]
    )

    assert generator is not None
    assert isinstance(generator, UnifiedDocGenerator)

    print("✓ Unified Documentation Generator created successfully")

    return True


def test_generators():
    """Test individual generators."""
    print("\nTesting individual generators...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Test CommandDocGenerator
    cmd_gen = CommandDocGenerator(registry)
    commands = cmd_gen.extract_commands()
    print(f"✓ CommandDocGenerator: {len(commands)} domains")

    # Test RouteDocGenerator
    route_gen = RouteDocGenerator(registry)
    routes = route_gen.extract_routes()
    print(f"✓ RouteDocGenerator: {len(routes)} routes")

    # Test ServiceDocGenerator
    svc_gen = ServiceDocGenerator(registry)
    services = svc_gen.extract_services()
    print(f"✓ ServiceDocGenerator: {len(services)} services")

    # Test SchemaDocGenerator
    schema_gen = SchemaDocGenerator(registry)
    schemas = schema_gen.extract_schemas()
    print(f"✓ SchemaDocGenerator: {len(schemas)} schemas")

    return True


def test_markdown_generation():
    """Test Markdown generation."""
    print("\nTesting Markdown generation...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Test CommandDocGenerator markdown
    cmd_gen = CommandDocGenerator(registry)
    cmd_md = cmd_gen.generate_markdown()

    assert "# EE Gateway Commands Documentation" in cmd_md
    assert "## " in cmd_md  # Has sections
    print("✓ Command Markdown generated successfully")

    # Test RouteDocGenerator markdown
    route_gen = RouteDocGenerator(registry)
    route_md = route_gen.generate_markdown()

    assert "# EE Gateway Routes Documentation" in route_md
    print("✓ Route Markdown generated successfully")

    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("EE Doc Gateway Integration Tests")
    print("=" * 60)

    tests = [
        ("Import Test", test_doc_gateway_import),
        ("Domain Creation", test_doc_gateway_domain),
        ("Registration", test_doc_gateway_registration),
        ("Routes", test_doc_gateway_routes),
        ("Unified Generator", test_unified_generator),
        ("Individual Generators", test_generators),
        ("Markdown Generation", test_markdown_generation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {name} failed: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
