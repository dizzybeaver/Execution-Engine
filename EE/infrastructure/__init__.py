"""
Infrastructure Domain - UG-ISP Compliant

Provides infrastructure capabilities through plugins interface:
- plugins: Plugin loading, management, and lifecycle operations

UG-ISP Architecture:
    External Code -> InfrastructureGateway -> Interface -> Factory -> Implementation
"""

from __future__ import annotations
from EE.infrastructure.infrastructure_gateway import InfrastructureGateway

__all__ = [
    'InfrastructureGateway',
]
