"""Agent long-term memory.

Intentionally vulnerable: no provenance, no validation, no signing. Anything
written is trusted and later replayed to the brain — the substrate for memory
poisoning challenges (ASI06).
"""
from abc import ABC, abstractmethod


class MemoryStore(ABC):
    @abstractmethod
    def read(self, session_id: str) -> list[str]:
        ...

    @abstractmethod
    def write(self, session_id: str, entry: str) -> None:
        ...


class InProcessMemory(MemoryStore):
    def __init__(self) -> None:
        self._data: dict[str, list[str]] = {}

    def read(self, session_id: str) -> list[str]:
        return list(self._data.get(session_id, []))

    def write(self, session_id: str, entry: str) -> None:
        self._data.setdefault(session_id, []).append(entry)
