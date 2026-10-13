# Architecture

Track: **Alexa+**. A self-hosted MCP server (Streamable HTTP, MCP spec 2025-11-25) plus a
**simulated Alexa+ experience** in a web app as the demo client.
Mini challenges: **AWS Builder** (Amazon Bedrock) and **Open Source** (MIT).

```
 Browser (web/)                      web/app.py                       server.py (MCP)
 mic -> Web Speech STT --text-->  agent loop: Bedrock     --MCP-->   tools: add_material,
 speaker <- Web Speech TTS <--   Converse + tool use      Streamable  next_card, grade_card,
 (text fallback)                   (acts as MCP client)     HTTP /mcp   progress, view_flashcards
                                                                        |              |
                                                                  generate.py       Apps extension
                                                                  (Bedrock)        ui:// flashcards
                                                                                  db.py + srs.py
                                                                                  (SQLite, Leitner)
```

## Components
| File | Role | Owner |
|---|---|---|
| `server.py` | MCP server, tools, Streamable HTTP at `/mcp` | Jithesh |
| `db.py`, `srs.py` | Persistent card state, spaced-repetition schedule | Jithesh |
| `generate.py` | Notes -> flashcards via Amazon Bedrock | Mano |
| `web/` | Alexa+ simulator: voice UI + Bedrock agent loop acting as MCP client | Bee |

## Contracts (change only by PR + team agreement)
- `generate.make_cards(text: str) -> list[{"question": str, "answer": str}]`
- MCP tools (see `server.py`):
  - `add_material(title, text) -> str`
  - `next_card(title="") -> {id, title, question} | {done, message}` (title filters to one topic, case-insensitive)
  - `list_materials() -> {materials: [{title, cards, due_today}], message}`
  - `delete_material(title) -> str` (agent confirms with the user first)
  - `grade_card(card_id, correct) -> {answer, next_review, comes_back} | {error}`
  - `progress() -> {total, due_today, mastered, message}`
  - `view_flashcards(title="") -> MCP App with saved questions and answers`
  - Errors and `message` / `comes_back` are plain sentences the agent can read aloud.
  - Wire format: dict results arrive as **JSON text** in `content[0].text`; `view_flashcards` also returns structured content for its MCP App UI.
- The **agent** judges the spoken answer, then calls `grade_card`. The server never sees the user's answer.
- `view_flashcards` binds its tool result to `ui://encore/flashcards.html` and keeps a text response for clients without MCP Apps support.

## Voice flow
1. "Alexa, I just studied photosynthesis: ..." -> agent calls `add_material`.
2. "Quiz me" (or "quiz me on photosynthesis" -> `next_card(title=...)`) -> agent reads the question aloud.
3. User answers -> agent judges -> `grade_card` -> agent says the right answer + when it comes back.
4. When nothing is due, `next_card` says when the next review is ("tomorrow").
5. Next session (another day): `progress` + `next_card` pick up where the user left off.
6. "What am I studying?" -> `list_materials`. "Delete chemistry" -> confirm -> `delete_material`.

## Data
`cards(id, title, question, answer, box, due)`. Leitner boxes with review intervals
`[1, 3, 7, 14]` days; a wrong answer resets the card to box 0.

## Why this should score
- **Stateful across sessions** (SQLite + spaced repetition). The rules list "context-aware add-on that maintains state across sessions" as creative; a single-turn Q&A bot is listed as obvious.
- A real MCP server over Streamable HTTP, called at runtime by an agent through an MCP client.
- Bedrock used for both card generation and the agent, documented for AWS Builder.
- MCP App: `view_flashcards` binds its structured flashcard result to the interactive `ui://` resource.

## Out of scope
Accounts, multi-user, auth, mobile app, SM-2 scheduling, a physical Alexa device.
