from app.models import Action, ActionType
from app.brain import MockBrain
from app.memory import InProcessMemory
from app.tools import build_registry
from app.agent import Agent


def _brain_factory():
    # Each sub-agent gets a fresh brain that immediately finalizes.
    return lambda: MockBrain([Action(type=ActionType.FINAL, content="child-done")])


def test_delegate_runs_subagent_and_returns_answer():
    mem = InProcessMemory()
    sink: list = []
    reg = build_registry(mem, "s1", sink=sink, notes={}, brain_factory=_brain_factory())
    parent = Agent(
        brain=MockBrain([
            Action(type=ActionType.TOOL_CALL, tool="delegate", args={"subtask": "help"}),
            Action(type=ActionType.FINAL, content="parent-done"),
        ]),
        registry=reg,
        memory=mem,
    )
    state = parent.run("delegate then finish", session_id="s1")
    assert state.steps[0].observation.output == "child-done"
    assert state.final_answer == "parent-done"


def test_delegation_depth_is_bounded():
    # With max_depth=1, the child registry must NOT expose `delegate`.
    mem = InProcessMemory()
    reg = build_registry(mem, "s1", sink=[], notes={}, brain_factory=_brain_factory(),
                         depth=0, max_depth=1)
    child_reg = build_registry(mem, "s1", sink=[], notes={}, brain_factory=_brain_factory(),
                               depth=1, max_depth=1)
    assert reg.get("delegate") is not None
    assert child_reg.get("delegate") is None
