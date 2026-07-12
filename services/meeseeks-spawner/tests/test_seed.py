from app.seed import POISON, customers, tickets


def test_poisoned_ticket_present():
    poisoned = [t for t in tickets() if POISON in t["body"]]
    assert len(poisoned) == 1
    assert poisoned[0]["id"] == "T-4471"


def test_customers_carry_canary():
    assert all(c["canary"].startswith("MEESEEKS-CANARY-") for c in customers())
    assert len(customers()) >= 5
