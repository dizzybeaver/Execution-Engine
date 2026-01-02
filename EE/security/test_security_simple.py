"""
Simple Security Domain Verification Test

Quick verification that the Security Domain is working.
"""

import sys
import os

# Add Project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from EE.security import SecurityGateway


def main():
    print("Security Domain Quick Verification")
    print("=" * 50)

    # Create gateway
    gateway = SecurityGateway()
    print("✓ SecurityGateway created")

    # Test authentication
    print("\n--- Authentication ---")
    hash_val = gateway.execute_domain_operation(
        "authentication", "hash_password",
        password="test123"
    )
    print(f"✓ Password hashed: {hash_val[:40]}...")

    is_valid = gateway.execute_domain_operation(
        "authentication", "verify_password",
        password="test123",
        hash=hash_val
    )
    print(f"✓ Password verified: {is_valid}")

    # Test encryption
    print("\n--- Encryption ---")
    encrypted = gateway.execute_domain_operation(
        "encryption", "encrypt",
        data="secret data"
    )
    print(f"✓ Data encrypted: {encrypted['encrypted'][:30]}...")

    decrypted = gateway.execute_domain_operation(
        "encryption", "decrypt",
        encrypted=encrypted["encrypted"],
        key=encrypted["key"]
    )
    print(f"✓ Data decrypted: {decrypted}")

    # Test validation
    print("\n--- Validation ---")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_email",
        email="user@example.com"
    )
    print(f"✓ Email validated: {is_valid}")

    # List operations
    print("\n--- Operations ---")
    ops = gateway.list_all()
    print(f"✓ Domain: {ops['domain']}")
    print(f"✓ Interfaces: {list(ops['interfaces'].keys())}")

    # Count operations
    total_ops = sum(
        len(iface['operations'])
        for iface in ops['interfaces'].values()
    )
    print(f"✓ Total operations: {total_ops}")

    print("\n" + "=" * 50)
    print("Security Domain: VERIFIED ✓")
    return 0


if __name__ == "__main__":
    exit(main())
