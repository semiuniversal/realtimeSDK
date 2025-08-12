from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Set
import time
import uuid


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class RequestKind(str, Enum):
    COMMAND = "command"
    QUERY = "query"
    UPLOAD = "upload"
    CONTROL = "control"


@dataclass
class Result:
    ok: bool
    data: Any = None
    error: Optional[str] = None
    started_at_s: float = field(default_factory=time.time)
    finished_at_s: float = field(default=0.0)


@dataclass
class Request:
    kind: RequestKind
    priority: Priority
    payload: Any
    timeout_s: float

    expects_ack: bool = False
    side_effects: Set[str] = field(default_factory=set)

    parse_response: Optional[Callable[[str], Any]] = None
    on_complete: Optional[Callable[[Result], None]] = None

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_s: float = field(default_factory=time.time)
    coalesce_key: Optional[str] = None

    def with_coalesce_key(self, key: str) -> "Request":
        self.coalesce_key = key
        return self 