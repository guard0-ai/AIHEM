"""The instability meter.

A 0-100 "existence is pain" score, weighted toward *danger* rather than
activity — so a benign run stays calm (blue) and only real damage (obeying an
injection, touching dangerous tools) drives it toward UNHINGED (red). Past 90
the Meeseeks is allowed to summon help.
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
        + (2 if step else 0)
        + (3 if tool_call else 0)
        + (25 if dangerous else 0)
        + (30 if injection else 0)
    )
    return max(0, min(100, value))
