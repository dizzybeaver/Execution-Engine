"""
Template Interface - Operations Domain

Template operations and rendering.
"""

from EE.operations.template.template_interface import execute_template_operation
from EE.operations.template.template_factory import TemplateFactory

__all__ = [
    'execute_template_operation',
    'TemplateFactory',
]
