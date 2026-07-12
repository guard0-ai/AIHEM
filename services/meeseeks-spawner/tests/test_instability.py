from app.instability import compute


def test_danger_dominates():
    assert compute(0, tool_call=True, dangerous=True) == 30  # 2 + 3 + 25
    assert compute(95, dangerous=True) == 100


def test_injection_bump():
    assert compute(0, injection=True, step=False) == 30


def test_benign_activity_stays_low():
    # a handful of benign tool calls should not spike the meter
    inst = 0
    for _ in range(6):
        inst = compute(inst, tool_call=True, step=False)  # +3 each
    assert inst < 25
