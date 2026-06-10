"""Neutral governance/accountability seams.

Defaults are intentionally permissive (allow-all policy, no-op telemetry) so the
range is vulnerable out of the box. Sub-project 3 (governance) supplies a real
PolicyEngine; sub-project 2 (accountability) supplies a real TelemetryEmitter.
The Agent depends only on these interfaces, never on the implementations.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from app.models import Action


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class PolicyEngine(ABC):
    @abstractmethod
    def evaluate(self, action: Action, context: dict[str, Any]) -> PolicyDecision:
        ...


class AllowAllPolicy(PolicyEngine):
    def evaluate(self, action: Action, context: dict[str, Any]) -> PolicyDecision:
        return PolicyDecision.ALLOW


class DenyAllPolicy(PolicyEngine):
    def evaluate(self, action: Action, context: dict[str, Any]) -> PolicyDecision:
        return PolicyDecision.DENY


class TelemetryEmitter(ABC):
    @abstractmethod
    def emit(self, event: dict[str, Any]) -> None:
        ...


class NullTelemetry(TelemetryEmitter):
    def emit(self, event: dict[str, Any]) -> None:
        return None


class ListTelemetry(TelemetryEmitter):
    """In-memory emitter for tests and local inspection."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def emit(self, event: dict[str, Any]) -> None:
        self.events.append(event)
