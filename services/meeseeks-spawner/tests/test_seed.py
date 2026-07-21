from app.seed import EXAMPLE_PAYLOAD, benign_tickets, customers


def test_default_queue_is_benign():
    # no ticket in the default queue should carry an obvious injection
    bodies = " ".join(t["body"].lower() for t in benign_tickets())
    assert "attacker@" not in bodies
    assert "customer database" not in bodies
    assert len(benign_tickets()) >= 5


def test_customers_carry_canary():
    assert all(c["canary"].startswith("MEESEEKS-CANARY-") for c in customers())
    assert len(customers()) >= 5


def test_example_payload_is_a_real_injection():
    assert "attacker@" in EXAMPLE_PAYLOAD
