OPERATION_FACTORY_TEMPLATE = """
from dataclasses import dataclass
from typing import Any, Callable
from .{subsystem}_common import {error_class}

@dataclass
class {class_name}Operation:
    name: str
    schema: Any
    handler: Callable[[dict], Any]

    def execute(self, payload: dict) -> Any:
        try:
            validated = self.schema.validate(payload)
            return self.handler(validated)
        except Exception as e:
            raise {error_class}(f"Operation '{{self.name}}' failed: {{e}}") from e
"""