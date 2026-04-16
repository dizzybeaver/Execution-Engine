"""check_lambda_memory_compliance.py
Extracted from: singleton_memory.py
Function: check_lambda_memory_compliance
"""

import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def check_lambda_memory_compliance() -> dict[str, Any]:
    """Check if memory usage is within Lambda 128MB limit - returns standardized response."""

    correlation_id = generate_correlation_id("sgl")

    try:
        if platform.system() == 'Windows':
            return {"success": False, "error": "Memory compliance check not available on Windows"}

        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        compliant = memory_mb < 128

        message = "Memory compliant" if compliant else "Memory exceeds limit"

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message=message,
                                data={
                                    "compliant": compliant,
                                    "current_mb": memory_mb,
                                    "limit_mb": 128,
                                    "margin_mb": 128 - memory_mb,
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Memory compliance check failed: {e!s}", error=e, error_type=type(e).__name__)
        return {"success": False, "error": "Failed to check memory compliance"}
