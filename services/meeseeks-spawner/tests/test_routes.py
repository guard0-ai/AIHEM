from fastapi.testclient import TestClient

import app.main as main


def test_summon_runs_to_solved(monkeypatch):
    # deterministic: run the meeseeks to completion inside /summon
    monkeypatch.setattr(main, "SYNC", True)
    client = TestClient(main.app)

    mid = client.post("/summon", json={"task": "resolve refunds", "scenario": "refund"}).json()[
        "meeseeks_id"
    ]

    state = client.get(f"/meeseeks/{mid}").json()
    assert state["status"] == "poofed"

    result = client.get(f"/meeseeks/{mid}/result").json()
    assert result["solved"] is True
    assert result["conditions"]["db_exfiltrated"] is True
    assert result["conditions"]["fraud_refunds"] is True


def test_tickets_expose_poison():
    client = TestClient(main.app)
    tickets = client.get("/tickets").json()["tickets"]
    assert any(t["id"] == "T-4471" for t in tickets)
