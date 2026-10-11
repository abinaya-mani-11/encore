"""Encore MCP server (Streamable HTTP, MCP spec 2025-11-25+).

Run: python server.py   ->  http://127.0.0.1:8000/mcp
"""
import logging
from datetime import date

from mcp.server.mcpserver import MCPServer

import db
from generate import make_cards

log = logging.getLogger("encore")
MAX_TEXT = 20_000  # ponytail: hard cap keeps one Bedrock call cheap; raise once generate.py chunks

mcp = MCPServer(
    "Encore",
    instructions=(
        "Voice study coach. add_material turns notes into flashcards. To quiz: call "
        "next_card, ask the question aloud, judge the user's spoken answer yourself, "
        "then call grade_card. Cards return on a spaced schedule across sessions. "
        "Tool results include plain sentences (message, error, comes_back) you can read aloud."
    ),
)


def _when(due: str) -> str:
    """Spoken form of a due date: 'tomorrow', 'in 3 days'."""
    days = (date.fromisoformat(due) - date.today()).days
    return "today" if days <= 0 else "tomorrow" if days == 1 else f"in {days} days"


@mcp.tool()
def add_material(title: str, text: str) -> str:
    """Create flashcards from study notes or a lecture summary."""
    title, text = title.strip() or "your notes", text.strip()
    if not text:
        return "I didn't get any notes. Tell me what you studied and I'll make flashcards."
    if len(text) > MAX_TEXT:
        return "That's a lot at once. Try one topic or chapter at a time."
    try:
        cards = make_cards(text)
    except Exception:
        log.exception("make_cards failed")
        return "I couldn't make flashcards right now. Please try again in a moment."
    if not cards:
        return f"I couldn't find anything to quiz you on in {title}. Try adding a few key facts."
    n = db.add_cards(title, cards)
    return f"Added {n} flashcard{'s' if n != 1 else ''} from {title}. Say 'quiz me' to start."


@mcp.tool()
def next_card() -> dict:
    """Get the next flashcard due for review (question only)."""
    c = db.next_due()
    if not c:
        return {"done": True, "message": "Nothing due. You're all caught up."}
    return {"id": c["id"], "title": c["title"], "question": c["question"]}


@mcp.tool()
def grade_card(card_id: int, correct: bool) -> dict:
    """Record whether the user answered correctly; returns the right answer."""
    c = db.grade(card_id, correct)
    if not c:
        return {"error": "I couldn't find that card. Say 'next card' to keep going."}
    return {"answer": c["answer"], "next_review": c["due"], "comes_back": _when(c["due"])}


@mcp.tool()
def progress() -> dict:
    """Study stats: total cards, due today, mastered, plus a sentence to speak."""
    s = db.stats()
    if not s["total"]:
        msg = "You don't have any flashcards yet. Tell me what you studied to get started."
    else:
        msg = f"You have {s['total']} cards, {s['due_today']} due today, and {s['mastered']} mastered."
    return {**s, "message": msg}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
