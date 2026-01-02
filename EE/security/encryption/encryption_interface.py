"""
Encryption Interface Router - Security Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.security.encryption.encryption_factory import EncryptionFactory


def execute_encryption_operation(operation: str, **kwargs) -> Any:
    """
    Execute encryption operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (encrypt, decrypt, hash, etc.)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # Get injected dependencies
    logger = kwargs.get("logger")
    metrics = kwargs.get("metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance
    factory = EncryptionFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'encrypt': factory.encrypt,
        'decrypt': factory.decrypt,
        'hash': factory.hash,
        'hash_sha512': factory.hash_sha512,
        'hash_md5': factory.hash_md5,
        'verify_hash': factory.verify_hash,
        'generate_key': factory.generate_key,
        'generate_salt': factory.generate_salt,
        'encode_base64': factory.encode_base64,
        'decode_base64': factory.decode_base64,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown encryption operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_encryption_operation',
]
