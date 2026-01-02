# factory_registry.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

@dataclass
class FactoryInfo:
    name: str
    subsystem: str
    type: str
    path: Path
    doc_path: Path
    test_path: Path
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)

@dataclass
class FactoryRegistry:
    factories: Dict[str, FactoryInfo] = field(default_factory=dict)

    def register(self, info: FactoryInfo):
        key = f"{info.subsystem}.{info.name}"
        self.factories[key] = info

    def list(self):
        return {k: vars(v) for k, v in self.factories.items()}

    def find_by_subsystem(self, subsystem: str):
        return {
            k: vars(v)
            for k, v in self.factories.items()
            if v.subsystem == subsystem
        }

    def find_by_type(self, type: str):
        return {
            k: vars(v)
            for k, v in self.factories.items()
            if v.type == type
        }