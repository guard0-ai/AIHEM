from app.instability import compute


def test_rises_and_clamps():
    assert compute(0, tool_call=True, dangerous=True) == 43  # 10 + 8 + 25
    assert compute(95, dangerous=True) == 100


def test_injection_bump():
    assert compute(0, injection=True, step=False) == 15
