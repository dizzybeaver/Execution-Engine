"""
Security Domain Gateway - UG-ISP Compliant

Routes operations to appropriate interfaces within the Security domain:
- authentication: Authentication and authorization
- encryption: Data encryption and hashing
- validation: Input validation and sanitization

UG-ISP Compliance:
- Extends DomainGateway base class
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
"""

from __future__ import annotations
from typing import Any, Dict, Callable

# EE 2.1: NO sys.path manipulation
from EE.universal_gateway.domain_gateway import DomainGateway

# Import interface routers
from EE.security.authentication.authentication_interface import execute_authentication_operation
from EE.security.encryption.encryption_interface import execute_encryption_operation
from EE.security.validation.validation_interface import execute_validation_operation


class SecurityGateway(DomainGateway):
    """Security Domain Gateway - EE 2.1 Compliant.

    Provides security capabilities through the following interfaces:
    - authentication: Authentication and authorization (verify, hash, token, authorize)
    - encryption: Data encryption and hashing (encrypt, decrypt, hash, verify)
    - validation: Input validation and sanitization (validate, sanitize, check)

    All operations follow UG-ISP patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside security domain

    Example:
        gateway = SecurityGateway(
            domain_name="security",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=callback
        )

        # Verify password
        is_valid = gateway.execute_domain_operation(
            "authentication", "verify_password",
            password="secret123",
            hash="$2b$12$..."
        )

        # Encrypt data
        encrypted = gateway.execute_domain_operation(
            "encryption", "encrypt",
            data="sensitive data",
            key="encryption-key"
        )

        # Validate email
        is_valid = gateway.execute_domain_operation(
            "validation", "validate_email",
            email="user@example.com"
        )
    """

    # FIXED: Removed @dataclass(frozen=True) decorator - incompatible with custom __init__
    # FIXED: Removed dataclass field declarations (logger, metrics, call_operation)

    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        """Initialize security domain gateway (EE 2.1).

        Args:
            domain_name: Domain name (must be "security")
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        # Call parent constructor with uniform signature (EE 2.1)
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    # FIXED: Removed legacy execute() method - use execute_domain_operation() instead

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using UG-ISP pattern.

        Args:
            interface: Interface name (authentication, encryption, validation)
            operation: Operation name (verify_password, encrypt, validate_email, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            GatewayError: If interface or operation is invalid
        """
        # EE 2.1: Inject factory functions instead of instances
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("call_operation", self._call_operation)

        # Route to appropriate interface
        try:
            if interface == "authentication":
                return execute_authentication_operation(operation, **kwargs)
            elif interface == "encryption":
                return execute_encryption_operation(operation, **kwargs)
            elif interface == "validation":
                return execute_validation_operation(operation, **kwargs)
            else:
                raise GatewayError(
                    f"Unknown security interface: {interface}. "
                    f"Valid interfaces: authentication, encryption, validation"
                )
        except ValueError as e:
            raise GatewayError(
                f"Operation failed: {e}"
            ) from e

    def list_all(self) -> Dict[str, Any]:
        """List all security domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": "security",
            "interfaces": {
                "authentication": {
                    "description": "Authentication and authorization",
                    "operations": [
                        {"operation": "hash_password", "description": "Hash password with bcrypt"},
                        {"operation": "verify_password", "description": "Verify password against hash"},
                        {"operation": "generate_token", "description": "Generate JWT token"},
                        {"operation": "verify_token", "description": "Verify JWT token"},
                        {"operation": "decode_token", "description": "Decode JWT token without verification"},
                        {"operation": "authorize", "description": "Check authorization permissions"},
                        {"operation": "generate_api_key", "description": "Generate API key"},
                        {"operation": "verify_api_key", "description": "Verify API key"},
                    ]
                },
                "encryption": {
                    "description": "Data encryption and hashing",
                    "operations": [
                        {"operation": "encrypt", "description": "Encrypt data with AES"},
                        {"operation": "decrypt", "description": "Decrypt AES encrypted data"},
                        {"operation": "hash", "description": "Generate SHA256 hash"},
                        {"operation": "hash_sha512", "description": "Generate SHA512 hash"},
                        {"operation": "hash_md5", "description": "Generate MD5 hash (legacy)"},
                        {"operation": "verify_hash", "description": "Verify data against hash"},
                        {"operation": "generate_key", "description": "Generate encryption key"},
                        {"operation": "generate_salt", "description": "Generate cryptographic salt"},
                        {"operation": "encode_base64", "description": "Encode to base64"},
                        {"operation": "decode_base64", "description": "Decode from base64"},
                    ]
                },
                "validation": {
                    "description": "Input validation and sanitization",
                    "operations": [
                        {"operation": "validate_email", "description": "Validate email format"},
                        {"operation": "validate_url", "description": "Validate URL format"},
                        {"operation": "validate_uuid", "description": "Validate UUID format"},
                        {"operation": "validate_ip", "description": "Validate IP address"},
                        {"operation": "validate_phone", "description": "Validate phone number"},
                        {"operation": "sanitize_string", "description": "Sanitize string input"},
                        {"operation": "sanitize_html", "description": "Sanitize HTML input"},
                        {"operation": "sanitize_sql", "description": "Escape SQL input"},
                        {"operation": "check_length", "description": "Check string length"},
                        {"operation": "check_range", "description": "Check numeric range"},
                        {"operation": "check_regex", "description": "Check regex match"},
                    ]
                },
            }
        }


__all__ = [
    "SecurityGateway",
]
