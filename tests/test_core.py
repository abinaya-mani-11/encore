import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["ENCORE_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")

import db
import srs
from generate import make_cards


def test_srs():
    d = date(2026, 1, 1)
    assert srs.review(0, True, d) == (1, d + timedelta(days=3))
    assert srs.review(3, True, d)[0] == 3  # capped
    assert srs.review(2, False, d) == (0, d + timedelta(days=1))


def test_flow():
    assert db.add_cards("t", make_cards("What is ATP? Cell energy currency")) == 1
    c = db.next_due()
    assert c["question"] == "What is ATP?"
    g = db.grade(c["id"], True)
    assert g["box"] == 1 and db.next_due() is None
    assert db.stats() == {"total": 1, "due_today": 0, "mastered": 0}


def test_server_validation():
    import server

    assert "didn't get any notes" in server.add_material("x", "   ")
    assert "one topic" in server.add_material("x", "a" * (server.MAX_TEXT + 1))
    assert "couldn't find anything" in server.add_material("x", "no questions here")
    assert "error" in server.grade_card(999999, True)

    import logging

    real = server.make_cards
    server.make_cards = lambda t: 1 / 0  # simulate a Bedrock failure
    logging.disable(logging.CRITICAL)
    try:
        assert "try again" in server.add_material("x", "What is ATP? energy")
    finally:
        server.make_cards = real
        logging.disable(logging.NOTSET)

    assert server.add_material("  ", "What is DNA? Genetic code").startswith("Added 1 flashcard from your notes")
    c = server.next_card()
    assert server.grade_card(c["id"], False)["comes_back"] == "tomorrow"
    assert "cards" in server.progress()["message"]


if __name__ == "__main__":
    test_srs(); test_flow(); test_server_validation(); print("ok")
