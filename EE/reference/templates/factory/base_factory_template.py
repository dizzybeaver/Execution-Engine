BASE_FACTORY_TEMPLATE = """
from dataclasses import dataclass
from typing import Any
from .{subsystem}_common import {error_class}

@dataclass
class {class_name}:
    \"""
    Factory: {class_name}
    Subsystem: {subsystem}
    Purpose: {purpose}
    \"""
    config: dict

    def create(self) -> Any:
        try:
            # TODO: Implement factory logic
            return {{}}
        except Exception as e:
            raise {error_class}(f"Failed to create {class_name}: {{e}}") from e


def create_{factory_name}(**config) -> {class_name}:
    return {class_name}(config=config)
"""