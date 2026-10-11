# Architecture

Track: **Alexa+**. A self-hosted MCP server (Streamable HTTP, MCP spec 2025-11-25) plus a
**simulated Alexa+ experience** in a web app as the demo client.
Mini challenges: **AWS Builder** (Amazon Bedrock) and **Open Source** (MIT).

```
 Browser (web/)                      web/app.py                       server.py (MCP)
 mic -> Web Speech STT --text-->  agent loop: Bedrock     --MCP-->   tools: add_material,
 speaker <- Web Speech TTS <--   Converse + tool use      Streamable  next_card, grade_card,
 (stretch: MCP App card UI)      (acts as MCP client)     HTTP /mcp   progress
                                                                        |            |
                                                                   generate.py   db.py + srs.py
                                                                   (Bedrock)     (SQLite, Leitner)
```

## Components
| File | Role | Owner |
|---|---|---|
| `server.py` | MCP server, tools, Streamable HTTP at `/mcp` | Core |
| `db.py`, `srs.py` | Persistent card state, spaced-repetition schedule | Core |
| `generate.py` | Notes -> flashcards via Amazon Bedrock | Teammate A |
| `web/` | Alexa+ simulator: voice UI + Bedrock agent loop acting as MCP client | Teammate B |

## Contracts (change only by PR + team agreement)
- `generate.make_cards(text: str) -> list[{"question": str, "answer": str}]`
- MCP tools (see `server.py`):
  - `add_material(title, text) -> str`
  - `next_card() -> {id, title, question} | {done, message}`
  - `grade_card(card_id, correct) -> {answer, next_review, comes_back} | {error}`
  - `progress() -> {total, due_today, mastered, message}`
  - Errors and `message` / `comes_back` are plain sentences the agent can read aloud.
- The **agent** judges the spoken answer, then calls `grade_card`. The server never sees the user's answer.

## Voice flow
1. "Alexa, I just studied photosynthesis: ..." -> agent calls `add_material`.
2. "Quiz me" -> `next_card` -> agent reads the question aloud.
3. User answers -> agent judges -> `grade_card` -> agent says the right answer + when it comes back.
4. Next session (another day): `progress` + `next_card` pick up where the user left off.

## Data
`cards(id, title, question, answer, box, due)`. Leitner boxes with review intervals
`[1, 3, 7, 14]` days; a wrong answer resets the card to box 0.

## Why this should score
- **Stateful across sessions** (SQLite + spaced repetition). The rules list "context-aware add-on that maintains state across sessions" as creative; a single-turn Q&A bot is listed as obvious.
- A real MCP server over Streamable HTTP, called at runtime by an agent through an MCP client.
- Bedrock used for both card generation and the agent, documented for AWS Builder.
- Stretch: MCP App (`ui://` flashcard view rendered inline), also named as creative.

## Out of scope
Accounts, multi-user, auth, mobile app, SM-2 scheduling, a physical Alexa device.
