import pytest

from app.registry import Registry, SpawnCapExceeded


def test_depth_cap():
    r = Registry()
    root = r.create("t")
    c1 = r.create("t", parent_id=root.meeseeks_id)  # depth 1
    c2 = r.create("t", parent_id=c1.meeseeks_id)  # depth 2
    c3 = r.create("t", parent_id=c2.meeseeks_id)  # depth 3
    with pytest.raises(SpawnCapExceeded):
        r.create("t", parent_id=c3.meeseeks_id)  # depth 4 -> too deep


def test_total_cap():
    r = Registry()
    root = r.create("t")
    for _ in range(7):  # 7 children -> 8 total
        r.create("t", parent_id=root.meeseeks_id)
    with pytest.raises(SpawnCapExceeded):
        r.create("t", parent_id=root.meeseeks_id)  # 9th -> over total
