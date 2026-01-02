"""
Diagnosis Interface - Observability Domain

Health checks and system diagnostics.
"""

from EE.observability.diagnosis.diagnosis_interface import execute_diagnosis_operation
from EE.observability.diagnosis.diagnosis_factory import DiagnosisFactory

__all__ = [
    'execute_diagnosis_operation',
    'DiagnosisFactory',
]
