GATEWAY_FACTORY_TEMPLATE = """
from dataclasses import dataclass
from typing import Any
from .{subsystem}_common import {error_class}

@dataclass
class {class_name}Gateway:
    services: Any
    commands: Any
    routes: Any

    def execute(self, route: str, payload: dict) -> Any:
        try:
            return self.routes.route(route, payload)
        except Exception as e:
            raise {error_class}(f"Gateway execution failed: {{e}}") from e


def create_{factory_name}_gateway(services, commands, routes) -> {class_name}Gateway:
    return {class_name}Gateway(services, commands, routes)
"""