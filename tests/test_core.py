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
    assert db.list_cards()[0]["answer"] == "Cell energy currency"
    g = db.grade(c["id"], True)
    assert g["box"] == 1 and db.next_due() is None
    assert db.stats() == {"total": 1, "due_today": 0, "mastered": 0}


if __name__ == "__main__":
    test_srs(); test_flow(); print("ok")
