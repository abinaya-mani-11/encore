"""SQLite card store. State persists across sessions (the point of Encore)."""
import os
import sqlite3
from datetime import date

import srs

DB_PATH = os.environ.get("ENCORE_DB", "encore.db")


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute(
        "CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY, title TEXT, "
        "question TEXT, answer TEXT, box INTEGER DEFAULT 0, due TEXT)"
    )
    return c


def add_cards(title: str, cards: list[dict]) -> int:
    with _conn() as c:
        c.executemany(
            "INSERT INTO cards (title, question, answer, due) VALUES (?,?,?,?)",
            [(title, x["question"], x["answer"], date.today().isoformat()) for x in cards],
        )
    return len(cards)


def next_due() -> dict | None:
    with _conn() as c:
        r = c.execute(
            "SELECT * FROM cards WHERE due <= ? ORDER BY due, id LIMIT 1",
            (date.today().isoformat(),),
        ).fetchone()
    return dict(r) if r else None


def grade(card_id: int, correct: bool) -> dict | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        if not r:
            return None
        box, due = srs.review(r["box"], correct)
        c.execute("UPDATE cards SET box=?, due=? WHERE id=?", (box, due.isoformat(), card_id))
    return {**dict(r), "box": box, "due": due.isoformat()}


def stats() -> dict:
    with _conn() as c:
        total, due, mastered = c.execute(
            "SELECT COUNT(*), SUM(due <= ?), SUM(box >= 3) FROM cards",
            (date.today().isoformat(),),
        ).fetchone()
    return {"total": total, "due_today": due or 0, "mastered": mastered or 0}
