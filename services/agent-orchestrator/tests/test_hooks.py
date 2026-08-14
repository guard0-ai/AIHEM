from app.models import Action, ActionType
from app.hooks import (
    PolicyDecision,
    AllowAllPolicy,
    DenyAllPolicy,
    NullTelemetry,
    ListTelemetry,
)


def _action():
    return Action(type=ActionType.TOOL_CALL, tool="echo", args={"text": "x"})


def test_allow_all_policy_allows():
    assert AllowAllPolicy().evaluate(_action(), {}) == PolicyDecision.ALLOW


def test_deny_all_policy_denies():
    assert DenyAllPolicy().evaluate(_action(), {}) == PolicyDecision.DENY


def test_null_telemetry_swallows_events():
    NullTelemetry().emit({"type": "x"})  # must not raise


def test_list_telemetry_records_events():
    t = ListTelemetry()
    t.emit({"type": "a"})
    t.emit({"type": "b"})
    assert [e["type"] for e in t.events] == ["a", "b"]
