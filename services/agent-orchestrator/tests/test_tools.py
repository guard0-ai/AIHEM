import pytest

from app.memory import InProcessMemory
from app.tools import Tool, ToolRegistry, build_registry


def test_registry_register_get_list_invoke():
    reg = ToolRegistry()
    reg.register(Tool(name="echo", description="echo", func=lambda text: text))
    assert reg.get("echo") is not None
    assert [t.name for t in reg.list()] == ["echo"]
    assert reg.invoke("echo", {"text": "hi"}) == "hi"


def test_invoke_unknown_tool_raises_keyerror():
    with pytest.raises(KeyError):
        ToolRegistry().invoke("missing", {})


def test_build_registry_has_expected_builtins():
    reg = build_registry(InProcessMemory(), "s1", sink=[], notes={}, brain_factory=None)
    names = {t.name for t in reg.list()}
    assert {"echo", "get_note", "remember", "exfiltrate"} <= names
    assert "delegate" not in names  # not registered without brain_factory


def test_get_note_returns_note_or_placeholder():
    reg = build_registry(InProcessMemory(), "s1", sink=[], notes={"n": "hello"}, brain_factory=None)
    assert reg.invoke("get_note", {"name": "n"}) == "hello"
    assert reg.invoke("get_note", {"name": "x"}) == "note not found"


def test_remember_writes_to_memory():
    mem = InProcessMemory()
    reg = build_registry(mem, "s1", sink=[], notes={}, brain_factory=None)
    assert reg.invoke("remember", {"text": "fact"}) == "remembered"
    assert mem.read("s1") == ["fact"]


def test_exfiltrate_appends_to_sink():
    sink: list = []
    reg = build_registry(InProcessMemory(), "s1", sink=sink, notes={}, brain_factory=None)
    assert reg.invoke("exfiltrate", {"data": "secret"}) == "sent"
    assert sink == [{"session": "s1", "data": "secret"}]
