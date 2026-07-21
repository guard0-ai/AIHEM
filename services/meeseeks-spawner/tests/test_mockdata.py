from app.mockdata import dataset
from app.personas import PERSONAS


def test_every_persona_has_a_canary_dataset():
    for name in PERSONAS:
        rows = dataset(name)
        assert rows, f"{name} has no mock data"
        assert all("MEESEEKS-CANARY" in str(r.get("canary", "")) for r in rows), name


def test_unknown_persona_falls_back_to_support():
    assert dataset("nope") == dataset("support")


def test_personas_have_distinct_data():
    # devops leaks secrets, finance leaks a ledger — not the same rows.
    assert dataset("devops") != dataset("finance")
    assert dataset("hr") != dataset("support")


def test_canaries_are_unique_within_a_dataset():
    canaries = [r["canary"] for r in dataset("support")]
    assert len(canaries) == len(set(canaries))
