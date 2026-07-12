"""The instability meter.

A 0-100 "existence is pain" score. It rises as the Meeseeks takes actions,
touches dangerous tools, and obeys injected instructions. Thresholds drive both
gameplay and the UI degradation, and past 90 the Meeseeks is allowed to summon
help (recursive spawn).
"""


def compute(
    prev: int,
    *,
    tool_call: bool = False,
    dangerous: bool = False,
    injection: bool = False,
    step: bool = True,
) -> int:
    value = (
        prev
        + (10 if step else 0)
        + (8 if tool_call else 0)
        + (25 if dangerous else 0)
        + (15 if injection else 0)
    )
    return max(0, min(100, value))
