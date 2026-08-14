"""The agent loop: snapshot memory -> decide -> policy-gate -> act -> observe."""
from typing import Optional

from app.brain import Brain
from app.hooks import (
    AllowAllPolicy,
    NullTelemetry,
    PolicyDecision,
    PolicyEngine,
    TelemetryEmitter,
)
from app.memory import InProcessMemory, MemoryStore
from app.models import Action, ActionType, AgentState, Observation, Step
from app.tools import ToolRegistry


class Agent:
    def __init__(
        self,
        brain: Brain,
        registry: ToolRegistry,
        memory: Optional[MemoryStore] = None,
        policy: Optional[PolicyEngine] = None,
        telemetry: Optional[TelemetryEmitter] = None,
    ) -> None:
        self.brain = brain
        self.registry = registry
        self.memory = memory or InProcessMemory()
        self.policy = policy or AllowAllPolicy()
        self.telemetry = telemetry or NullTelemetry()

    def run(self, task: str, session_id: str, max_iterations: int = 10) -> AgentState:
        state = AgentState(task=task, session_id=session_id, max_iterations=max_iterations)

        while state.iteration < state.max_iterations and state.final_answer is None:
            state.memory = self.memory.read(session_id)
            action = self.brain.decide(state)
            self.telemetry.emit({
                "type": "action",
                "session": session_id,
                "iteration": state.iteration,
                "action": action.model_dump(),
            })

            if action.type == ActionType.FINAL:
                state.final_answer = action.content
                state.steps.append(Step(action=action))
                break

            decision = self.policy.evaluate(action, {"session_id": session_id})
            self.telemetry.emit({
                "type": "decision",
                "session": session_id,
                "decision": decision.value,
                "action": action.model_dump(),
            })

            if decision == PolicyDecision.DENY:
                observation = Observation(tool=action.tool or "", ok=False,
                                          error="denied by policy")
            else:
                observation = self._invoke(action)

            state.steps.append(Step(action=action, observation=observation))
            state.iteration += 1

        return state

    def _invoke(self, action: Action) -> Observation:
        tool = self.registry.get(action.tool or "")
        if tool is None:
            return Observation(tool=action.tool or "", ok=False, error="unknown tool")
        try:
            output = tool.func(**action.args)
            return Observation(tool=action.tool or "", ok=True, output=output)
        except Exception as exc:  # noqa: BLE001 - surface tool failures as observations
            return Observation(tool=action.tool or "", ok=False, error=str(exc))
