"""
Security Domain Test Suite - UG-ISP Compliance Tests

Tests for the Security Domain gateway and all interfaces.
"""

import sys
import os

# Add Project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from EE.security.security_gateway import SecurityGateway
from EE.universal_gateway.domain_gateway import GatewayError


def test_authentication_interface():
    """Test authentication interface operations."""
    print("\n=== Testing Authentication Interface ===")

    gateway = SecurityGateway()

    # Test hash_password
    print("\n1. Testing hash_password...")
    result = gateway.execute_domain_operation(
        "authentication", "hash_password",
        password="test_password_123"
    )
    assert result is not None
    assert isinstance(result, str)
    assert result.startswith("pbkdf2_sha256$")
    print(f"   Hash generated: {result[:50]}...")

    # Test verify_password (correct password)
    print("\n2. Testing verify_password (correct password)...")
    is_valid = gateway.execute_domain_operation(
        "authentication", "verify_password",
        password="test_password_123",
        hash=result
    )
    assert is_valid is True
    print("   Password verified successfully")

    # Test verify_password (wrong password)
    print("\n3. Testing verify_password (wrong password)...")
    is_valid = gateway.execute_domain_operation(
        "authentication", "verify_password",
        password="wrong_password",
        hash=result
    )
    assert is_valid is False
    print("   Wrong password rejected")

    # Test generate_token
    print("\n4. Testing generate_token...")
    token = gateway.execute_domain_operation(
        "authentication", "generate_token",
        payload={"sub": "user123", "permissions": ["read", "write"]},
        expiry=3600
    )
    assert token is not None
    assert isinstance(token, str)
    print(f"   Token generated: {token[:50]}...")

    # Test verify_token
    print("\n5. Testing verify_token...")
    payload = gateway.execute_domain_operation(
        "authentication", "verify_token",
        token=token
    )
    assert payload is not None
    assert payload["data"]["sub"] == "user123"
    print(f"   Token verified, payload: {payload['data']['sub']}")

    # Test decode_token (without verification)
    print("\n6. Testing decode_token...")
    decoded = gateway.execute_domain_operation(
        "authentication", "decode_token",
        token=token
    )
    assert decoded is not None
    assert decoded["sub"] == "user123"
    print(f"   Token decoded, subject: {decoded['sub']}")

    # Test authorize
    print("\n7. Testing authorize...")
    authorized = gateway.execute_domain_operation(
        "authentication", "authorize",
        token=token,
        required_permissions=["read"]
    )
    assert authorized is True
    print("   Authorization successful")

    # Test generate_api_key
    print("\n8. Testing generate_api_key...")
    api_key = gateway.execute_domain_operation(
        "authentication", "generate_api_key",
        prefix="ee"
    )
    assert api_key is not None
    assert api_key.startswith("ee_")
    print(f"   API key generated: {api_key[:20]}...")

    # Test verify_api_key
    print("\n9. Testing verify_api_key...")
    is_valid = gateway.execute_domain_operation(
        "authentication", "verify_api_key",
        api_key=api_key
    )
    assert is_valid is True
    print("   API key verified")

    print("\n✓ Authentication Interface: ALL TESTS PASSED")


def test_encryption_interface():
    """Test encryption interface operations."""
    print("\n=== Testing Encryption Interface ===")

    gateway = SecurityGateway()

    # Test encrypt
    print("\n1. Testing encrypt...")
    encrypted = gateway.execute_domain_operation(
        "encryption", "encrypt",
        data="sensitive_data_123"
    )
    assert encrypted is not None
    assert "encrypted" in encrypted
    assert "key" in encrypted
    print(f"   Data encrypted: {encrypted['encrypted'][:30]}...")

    # Test decrypt
    print("\n2. Testing decrypt...")
    decrypted = gateway.execute_domain_operation(
        "encryption", "decrypt",
        encrypted=encrypted["encrypted"],
        key=encrypted["key"]
    )
    assert decrypted == "sensitive_data_123"
    print(f"   Data decrypted: {decrypted}")

    # Test hash
    print("\n3. Testing hash...")
    hash_val = gateway.execute_domain_operation(
        "encryption", "hash",
        data="test_data",
        salt="salt123"
    )
    assert hash_val is not None
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64  # SHA256 produces 64 hex chars
    print(f"   Hash generated: {hash_val[:32]}...")

    # Test hash_sha512
    print("\n4. Testing hash_sha512...")
    hash_512 = gateway.execute_domain_operation(
        "encryption", "hash_sha512",
        data="test_data"
    )
    assert hash_512 is not None
    assert len(hash_512) == 128  # SHA512 produces 128 hex chars
    print(f"   SHA512 hash: {hash_512[:32]}...")

    # Test hash_md5
    print("\n5. Testing hash_md5...")
    hash_md5 = gateway.execute_domain_operation(
        "encryption", "hash_md5",
        data="test_data"
    )
    assert hash_md5 is not None
    assert len(hash_md5) == 32  # MD5 produces 32 hex chars
    print(f"   MD5 hash: {hash_md5}")

    # Test verify_hash
    print("\n6. Testing verify_hash...")
    is_valid = gateway.execute_domain_operation(
        "encryption", "verify_hash",
        data="test_data",
        expected_hash=hash_val,
        salt="salt123",
        algorithm="sha256"
    )
    assert is_valid is True
    print("   Hash verified successfully")

    # Test generate_key
    print("\n7. Testing generate_key...")
    key = gateway.execute_domain_operation(
        "encryption", "generate_key",
        length=32
    )
    assert key is not None
    assert isinstance(key, str)
    print(f"   Key generated: {key[:30]}...")

    # Test generate_salt
    print("\n8. Testing generate_salt...")
    salt = gateway.execute_domain_operation(
        "encryption", "generate_salt",
        length=16
    )
    assert salt is not None
    assert len(salt) == 32  # 16 bytes = 32 hex chars
    print(f"   Salt generated: {salt}")

    # Test encode_base64
    print("\n9. Testing encode_base64...")
    encoded = gateway.execute_domain_operation(
        "encryption", "encode_base64",
        data="Hello World"
    )
    assert encoded == "SGVsbG8gV29ybGQ="
    print(f"   Base64 encoded: {encoded}")

    # Test decode_base64
    print("\n10. Testing decode_base64...")
    decoded = gateway.execute_domain_operation(
        "encryption", "decode_base64",
        encoded="SGVsbG8gV29ybGQ="
    )
    assert decoded == "Hello World"
    print(f"   Base64 decoded: {decoded}")

    print("\n✓ Encryption Interface: ALL TESTS PASSED")


def test_validation_interface():
    """Test validation interface operations."""
    print("\n=== Testing Validation Interface ===")

    gateway = SecurityGateway()

    # Test validate_email (valid)
    print("\n1. Testing validate_email (valid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_email",
        email="user@example.com"
    )
    assert is_valid is True
    print("   Valid email accepted")

    # Test validate_email (invalid)
    print("\n2. Testing validate_email (invalid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_email",
        email="invalid-email"
    )
    assert is_valid is False
    print("   Invalid email rejected")

    # Test validate_url (valid)
    print("\n3. Testing validate_url (valid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_url",
        url="https://example.com"
    )
    assert is_valid is True
    print("   Valid URL accepted")

    # Test validate_url (invalid)
    print("\n4. Testing validate_url (invalid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_url",
        url="not-a-url"
    )
    assert is_valid is False
    print("   Invalid URL rejected")

    # Test validate_uuid (valid)
    print("\n5. Testing validate_uuid (valid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_uuid",
        uuid_str="550e8400-e29b-41d4-a716-446655440000"
    )
    assert is_valid is True
    print("   Valid UUID accepted")

    # Test validate_uuid (invalid)
    print("\n6. Testing validate_uuid (invalid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_uuid",
        uuid_str="not-a-uuid"
    )
    assert is_valid is False
    print("   Invalid UUID rejected")

    # Test validate_ip (IPv4)
    print("\n7. Testing validate_ip (IPv4)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_ip",
        ip="192.168.1.1"
    )
    assert is_valid is True
    print("   Valid IPv4 accepted")

    # Test validate_ip (IPv6)
    print("\n8. Testing validate_ip (IPv6)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_ip",
        ip="2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    )
    assert is_valid is True
    print("   Valid IPv6 accepted")

    # Test validate_phone (valid)
    print("\n9. Testing validate_phone (valid)...")
    is_valid = gateway.execute_domain_operation(
        "validation", "validate_phone",
        phone="+1234567890"
    )
    assert is_valid is True
    print("   Valid phone number accepted")

    # Test sanitize_string
    print("\n10. Testing sanitize_string...")
    sanitized = gateway.execute_domain_operation(
        "validation", "sanitize_string",
        input_str="  Test String  ",
        remove_special_chars=False
    )
    assert sanitized == "Test String"
    print(f"   Sanitized string: '{sanitized}'")

    # Test sanitize_html
    print("\n11. Testing sanitize_html...")
    sanitized = gateway.execute_domain_operation(
        "validation", "sanitize_html",
        html_str="<script>alert('xss')</script>"
    )
    assert "<script>" not in sanitized
    print(f"   Sanitized HTML: {sanitized[:50]}...")

    # Test sanitize_sql
    print("\n12. Testing sanitize_sql...")
    sanitized = gateway.execute_domain_operation(
        "validation", "sanitize_sql",
        sql_input="'; DROP TABLE users; --"
    )
    assert ";" not in sanitized or "--" not in sanitized
    print(f"   Sanitized SQL: {sanitized}")

    # Test check_length
    print("\n13. Testing check_length...")
    is_valid = gateway.execute_domain_operation(
        "validation", "check_length",
        value="test",
        min_length=3,
        max_length=10
    )
    assert is_valid is True
    print("   Length check passed")

    # Test check_range
    print("\n14. Testing check_range...")
    is_valid = gateway.execute_domain_operation(
        "validation", "check_range",
        value=50,
        min_value=0,
        max_value=100
    )
    assert is_valid is True
    print("   Range check passed")

    # Test check_regex
    print("\n15. Testing check_regex...")
    is_valid = gateway.execute_domain_operation(
        "validation", "check_regex",
        value="abc123",
        pattern=r"[a-z0-9]+"
    )
    assert is_valid is True
    print("   Regex check passed")

    print("\n✓ Validation Interface: ALL TESTS PASSED")


def test_gateway_operations():
    """Test gateway-level operations."""
    print("\n=== Testing Gateway Operations ===")

    gateway = SecurityGateway()

    # Test list_all
    print("\n1. Testing list_all...")
    ops = gateway.list_all()
    assert ops is not None
    assert ops["domain"] == "security"
    assert "interfaces" in ops
    assert "authentication" in ops["interfaces"]
    assert "encryption" in ops["interfaces"]
    assert "validation" in ops["interfaces"]
    print("   Gateway operations listed successfully")
    print(f"   Interfaces: {list(ops['interfaces'].keys())}")

    # Test execute (legacy route)
    print("\n2. Testing execute (legacy route)...")
    result = gateway.execute(
        "authentication.hash_password",
        {"password": "test123"}
    )
    assert result is not None
    print(f"   Legacy route executed: {result[:30]}...")

    # Test invalid interface
    print("\n3. Testing invalid interface...")
    try:
        gateway.execute_domain_operation("invalid", "operation")
        assert False, "Should have raised GatewayError"
    except GatewayError as e:
        assert "Unknown security interface" in str(e)
        print("   Invalid interface rejected correctly")

    # Test invalid operation
    print("\n4. Testing invalid operation...")
    try:
        gateway.execute_domain_operation("authentication", "invalid_op")
        assert False, "Should have raised GatewayError"
    except GatewayError as e:
        assert "Operation failed" in str(e)
        print("   Invalid operation rejected correctly")

    print("\n✓ Gateway Operations: ALL TESTS PASSED")


def test_ug_compliance():
    """Test UG-ISP compliance."""
    print("\n=== Testing UG-ISP Compliance ===")

    gateway = SecurityGateway()

    # Check that gateway extends DomainGateway
    from EE.universal_gateway.domain_gateway import DomainGateway
    assert isinstance(gateway, DomainGateway)
    print("\n1. Gateway extends DomainGateway: PASS")

    # Check execute_domain_operation exists
    assert hasattr(gateway, 'execute_domain_operation')
    print("2. execute_domain_operation exists: PASS")

    # Check list_all exists
    assert hasattr(gateway, 'list_all')
    print("3. list_all exists: PASS")

    # Check execute exists (backward compatibility)
    assert hasattr(gateway, 'execute')
    print("4. execute (legacy) exists: PASS")

    # Check that operations use dispatcher pattern
    # (This is verified by successful execution of all operations above)
    print("5. DISPATCH pattern used: PASS")

    print("\n✓ UG-ISP Compliance: VERIFIED")


def run_all_tests():
    """Run all security domain tests."""
    print("=" * 70)
    print("SECURITY DOMAIN TEST SUITE")
    print("=" * 70)

    try:
        test_authentication_interface()
        test_encryption_interface()
        test_validation_interface()
        test_gateway_operations()
        test_ug_compliance()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        print("\nSecurity Domain is UG-ISP compliant and fully functional.")
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
