from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable


@dataclass
class ComponentAlias:
    component_id: str
    function: str
    type: str
    description: str
    config: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = {}

    @property
    def hardware_type(self) -> str:
        return self.component_id.split(':')[0] if ':' in self.component_id else ""

    @property
    def hardware_id(self) -> str:
        return self.component_id.split(':')[1] if ':' in self.component_id else self.component_id

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "function": self.function,
            "type": self.type,
            "description": self.description,
        }
        data.update(self.config or {})
        return data


class CompositeFunction:
    """A simple composite function registry for high-level operations.

    This is a trimmed version that allows registering a name -> callable
    mapping so apps can look up higher-level behaviors by semantic name.
    """

    def __init__(self, name: str, handler: Callable[..., Any]) -> None:
        self.name = name
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


class AliasSystem:
    """Minimal alias system that stores aliases in-memory.

    In the full system this could load/save YAML, validate components, etc.
    For the trimmed distribution we keep it simple and dependency-free.
    """

    def __init__(self) -> None:
        self._aliases: Dict[str, ComponentAlias] = {}
        self._functions: Dict[str, CompositeFunction] = {}

    def add_alias(self, name: str, alias: ComponentAlias) -> None:
        self._aliases[name] = alias

    def get_alias(self, name: str) -> Optional[ComponentAlias]:
        return self._aliases.get(name)

    def list_aliases(self) -> List[str]:
        return list(self._aliases.keys())

    def register_function(self, name: str, handler: Callable[..., Any]) -> None:
        self._functions[name] = CompositeFunction(name, handler)

    def get_function(self, name: str) -> Optional[CompositeFunction]:
        return self._functions.get(name)

    def list_functions(self) -> List[str]:
        return list(self._functions.keys()) 