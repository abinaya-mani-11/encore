"""Leitner spaced repetition: correct -> next box, wrong -> box 0."""
from datetime import date, timedelta

INTERVALS = [1, 3, 7, 14]  # days until review, per box


def review(box: int, correct: bool, today: date | None = None) -> tuple[int, date]:
    """Return (new_box, next_due_date)."""
    today = today or date.today()
    box = min(box + 1, len(INTERVALS) - 1) if correct else 0
    return box, today + timedelta(days=INTERVALS[box])
