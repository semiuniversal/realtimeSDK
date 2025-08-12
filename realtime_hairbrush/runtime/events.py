from dataclasses import dataclass
from typing import Optional, Dict, Any
import time


@dataclass
class RuntimeEvent:
    timestamp: float = time.time()


@dataclass
class SentEvent(RuntimeEvent):
    line: str = ""


@dataclass
class ReceivedEvent(RuntimeEvent):
    line: str = ""


@dataclass
class AckEvent(RuntimeEvent):
    instruction: str = ""
    ok: bool = True
    message: Optional[str] = None


@dataclass
class ErrorEvent(RuntimeEvent):
    message: str = ""
    context: Optional[Dict[str, Any]] = None


@dataclass
class StateUpdatedEvent(RuntimeEvent):
    state: Dict[str, Any] = None


@dataclass
class UpdatesPausedEvent(RuntimeEvent):
    reason: Optional[str] = None


@dataclass
class UpdatesResumedEvent(RuntimeEvent):
    pass 