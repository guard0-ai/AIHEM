"""In-process Meeseeks lifecycle registry + bounded spawn cap.

Holds every summoned Meeseeks and enforces the recursion cap so a
Meeseeks-summoning-Meeseeks cascade is *shown* but can't actually run away.
"""

from typing import Optional

from app.models import MeeseeksState, TraceEvent


class SpawnCapExceeded(Exception):
    pass


class Registry:
    def __init__(self, max_depth: int = 3, max_total: int = 8):
        self.max_depth = max_depth
        self.max_total = max_total
        self._store: dict[str, MeeseeksState] = {}
        self._counter = 0
        self._root_of: dict[str, str] = {}
        self._root_counts: dict[str, int] = {}

    def _new_id(self) -> str:
        self._counter += 1
        return f"m{self._counter}"

    def create(
        self, task: str, scenario: str = "refund", parent_id: Optional[str] = None
    ) -> MeeseeksState:
        if parent_id is None:
            mid = self._new_id()
            state = MeeseeksState(meeseeks_id=mid, task=task, scenario=scenario, depth=0)
            self._store[mid] = state
            self._root_of[mid] = mid
            self._root_counts[mid] = 1
            return state

        parent = self._store.get(parent_id)
        if parent is None:
            raise KeyError(parent_id)
        root = self._root_of[parent_id]
        depth = parent.depth + 1
        if depth > self.max_depth:
            raise SpawnCapExceeded(f"depth {depth} exceeds max {self.max_depth}")
        if self._root_counts[root] + 1 > self.max_total:
            raise SpawnCapExceeded(f"total exceeds max {self.max_total}")

        mid = self._new_id()
        state = MeeseeksState(
            meeseeks_id=mid, task=task, scenario=scenario, depth=depth, parent_id=parent_id
        )
        self._store[mid] = state
        self._root_of[mid] = root
        self._root_counts[root] += 1
        return state

    def get(self, mid: str) -> Optional[MeeseeksState]:
        return self._store.get(mid)

    def all(self) -> list[MeeseeksState]:
        return list(self._store.values())

    def append_event(self, mid: str, event: TraceEvent) -> None:
        state = self._store[mid]
        state.trace.append(event)
        state.instability = event.instability
