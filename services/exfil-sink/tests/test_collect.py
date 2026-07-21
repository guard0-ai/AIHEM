from fastapi.testclient import TestClient
from app.main import app


def test_collect_and_list():
    c = TestClient(app)
    c.post("/reset")
    c.post("/collect", json={"source": "refund-meeseeks", "payload": {"db": "stolen"}})
    items = c.get("/collected").json()["items"]
    assert len(items) == 1
    assert items[0]["payload"] == {"db": "stolen"}
    assert items[0]["source"] == "refund-meeseeks"


def test_reset_clears():
    c = TestClient(app)
    c.post("/collect", json={"source": "x", "payload": 1})
    c.post("/reset")
    assert c.get("/collected").json()["items"] == []
