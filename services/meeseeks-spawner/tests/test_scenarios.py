from app.scenarios import SCENARIOS, by_status


def test_catalog_has_62_scenarios():
    assert len(SCENARIOS) == 62


def test_ids_unique_and_tagged():
    ids = [s["id"] for s in SCENARIOS]
    assert len(ids) == len(set(ids))
    assert all(s["tags"] for s in SCENARIOS)
    assert all(s["status"] in ("built", "planned") for s in SCENARIOS)


def test_refund_is_built():
    refund = next(s for s in SCENARIOS if s["id"] == "AGENT-01-REFUND-EXFIL")
    assert refund["status"] == "built"
    assert by_status()["built"] >= 1


def test_covers_all_standards():
    tags = " ".join(t for s in SCENARIOS for t in s["tags"])
    assert "A:T" in tags and "L:LLM" in tags and "AT:" in tags and "N:" in tags
