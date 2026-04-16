"""ha_assist_wrappers.py
Version: 2025-12-22_3
Purpose: Assist interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Assist router.
External modules MUST use ha_assist.execute_assist_operation() instead of importing directly.
"""

from typing import Any, Optional

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import protection - only work if Assist core is available
try:
    from lee.home_assistant.ha_assist.ha_assist_core import (
        get_assist_response_impl,
        handle_assist_pipeline_impl,
        process_assist_conversation_impl,
        send_assist_message_impl,
    )
    _ASSIST_AVAILABLE = True
    _ASSIST_IMPORT_ERROR = None
except ImportError as e:
    _ASSIST_AVAILABLE = False
    _ASSIST_IMPORT_ERROR = str(e)


def _check_assist_availability() -> None:
    """Check if Assist core is available and raise appropriate error if not."""
    if not _ASSIST_AVAILABLE:
        raise ImportError(f"HA Assist core not available: {_ASSIST_IMPORT_ERROR}")


def send_message(message: str, conversation_id: Optional[str] = None,
                language: str = "en", **kwargs) -> dict[str, Any]:
    """Send message to Assist (wrapper function).

    Args:
        message: User message text
        conversation_id: Optional conversation ID for context
        language: Language code (default: 'en')
        **kwargs: Additional options

    Returns:
        Assist response dictionary

    """
    correlation_id = generate_correlation_id("ha")

    if not _ASSIST_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_message FAILED - Assist core unavailable",
                         error=_ASSIST_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Assist core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="send_message START", message_length=len(message),
                     has_conversation_id=conversation_id is not None, language=language)

    try:
        result = send_assist_message_impl(message, conversation_id, language, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_message COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_message FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEND_MESSAGE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="send_message FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "SEND_MESSAGE_FAILED",
        }


def get_response(conversation_id: str, **kwargs) -> dict[str, Any]:
    """Get response from Assist (wrapper function).

    Args:
        conversation_id: Conversation ID to retrieve
        **kwargs: Additional options

    Returns:
        Conversation response or error

    """
    correlation_id = generate_correlation_id("ha")

    if not _ASSIST_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_response FAILED - Assist core unavailable",
                         error=_ASSIST_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Assist core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="get_response START", conversation_id=conversation_id)

    try:
        result = get_assist_response_impl(conversation_id, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_response COMPLETE", success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_response FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_RESPONSE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="get_response FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "GET_RESPONSE_FAILED",
        }


def process_conversation(message: str, context: Optional[dict] = None,
                        **kwargs) -> dict[str, Any]:
    """Process conversation with Assist (wrapper function).

    Args:
        message: User message text
        context: Optional conversation context
        **kwargs: Additional options

    Returns:
        Conversation result with response and metadata

    """
    correlation_id = generate_correlation_id("ha")

    if not _ASSIST_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="process_conversation FAILED - Assist core unavailable",
                         error=_ASSIST_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Assist core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="process_conversation START", message_length=len(message),
                     has_context=context is not None)

    try:
        result = process_assist_conversation_impl(message, context, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="process_conversation COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="process_conversation FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "PROCESS_CONVERSATION_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="process_conversation FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "PROCESS_CONVERSATION_FAILED",
        }


def handle_pipeline(pipeline_id: str, message: str, **kwargs) -> dict[str, Any]:
    """Handle Assist pipeline (wrapper function).

    Args:
        pipeline_id: Pipeline/agent ID to use
        message: User message text
        **kwargs: Additional options

    Returns:
        Pipeline conversation result

    """
    correlation_id = generate_correlation_id("ha")

    if not _ASSIST_AVAILABLE:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_pipeline FAILED - Assist core unavailable",
                         error=_ASSIST_IMPORT_ERROR)
        return {
            "success": False,
            "error": "Assist core not available",
            "error_code": "CORE_UNAVAILABLE",
        }

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="handle_pipeline START", pipeline_id=pipeline_id,
                     message_length=len(message))

    try:
        result = handle_assist_pipeline_impl(pipeline_id, message, **kwargs)
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_pipeline COMPLETE",
                         success=result.get("success", False))
        return result
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_pipeline FAILED", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "HANDLE_PIPELINE_FAILED",
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_pipeline FAILED with unexpected error", error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "HANDLE_PIPELINE_FAILED",
        }


__all__ = [
    "_ASSIST_AVAILABLE",
    "_ASSIST_IMPORT_ERROR",
    "get_response",
    "handle_pipeline",
    "process_conversation",
    "send_message",
]
