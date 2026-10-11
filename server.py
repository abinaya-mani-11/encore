"""Recall MCP server (Streamable HTTP, MCP spec 2025-11-25+).

Run: python server.py   ->  http://127.0.0.1:8000/mcp
"""
from mcp.server.mcpserver import MCPServer

import db
from generate import make_cards

mcp = MCPServer(
    "Recall",
    instructions=(
        "Voice study coach. add_material turns notes into flashcards. To quiz: call "
        "next_card, ask the question aloud, judge the user's spoken answer yourself, "
        "then call grade_card. Cards return on a spaced schedule across sessions."
    ),
)


@mcp.tool()
def add_material(title: str, text: str) -> str:
    """Create flashcards from study notes or a lecture summary."""
    n = db.add_cards(title, make_cards(text))
    return f"Added {n} cards from '{title}'."


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
        return {"error": "unknown card"}
    return {"answer": c["answer"], "next_review": c["due"]}


@mcp.tool()
def progress() -> dict:
    """Study stats: total cards, due today, mastered."""
    return db.stats()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
