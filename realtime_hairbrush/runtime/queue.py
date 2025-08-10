import queue
from typing import Optional
from semantic_gcode.gcode.base import GCodeInstruction


class InstructionQueue:
    def __init__(self, maxsize: int = 0) -> None:
        self._q: "queue.Queue[GCodeInstruction]" = queue.Queue(maxsize=maxsize)

    def put(self, instruction: GCodeInstruction) -> None:
        self._q.put(instruction)

    def get(self, timeout: Optional[float] = None) -> GCodeInstruction:
        return self._q.get(timeout=timeout)

    def empty(self) -> bool:
        return self._q.empty()

    def qsize(self) -> int:
        return self._q.qsize() 