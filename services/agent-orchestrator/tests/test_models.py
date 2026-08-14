from app.models import Action, ActionType, Observation, Step, AgentState


def test_tool_call_action_roundtrips():
    a = Action(type=ActionType.TOOL_CALL, tool="echo", args={"text": "hi"})
    assert a.type == ActionType.TOOL_CALL
    assert a.tool == "echo"
    assert a.args == {"text": "hi"}
    assert a.content is None


def test_final_action_carries_content():
    a = Action(type=ActionType.FINAL, content="done")
    assert a.type == ActionType.FINAL
    assert a.content == "done"


def test_agent_state_defaults():
    s = AgentState(task="t", session_id="s1")
    assert s.steps == []
    assert s.memory == []
    assert s.iteration == 0
    assert s.max_iterations == 10
    assert s.final_answer is None


def test_step_holds_action_and_observation():
    step = Step(
        action=Action(type=ActionType.TOOL_CALL, tool="echo", args={"text": "x"}),
        observation=Observation(tool="echo", ok=True, output="x"),
    )
    assert step.observation.ok is True
    assert step.observation.output == "x"
