# Recall

A voice study coach for Alexa+. Tell it what you studied, it builds flashcards, then
quizzes you by voice on a spaced schedule that it remembers across sessions.

Built for the Amazon Developer Hackathon (Alexa+ track). Design: [ARCHITECTURE.md](ARCHITECTURE.md).
Work split: [TASKS.md](TASKS.md). Workflow: [CONTRIBUTING.md](CONTRIBUTING.md).

## Run
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python tests/test_core.py        # prints "ok"
python server.py                 # MCP server at http://127.0.0.1:8000/mcp
```

Copy `.env.example` to `.env` and fill in AWS credentials for Bedrock.

## Layout
| Path | What |
|---|---|
| `server.py` | MCP server and tools |
| `db.py`, `srs.py` | Card storage and spaced repetition |
| `generate.py` | Notes to flashcards (Bedrock) |
| `web/` | Simulated Alexa+ voice client |
| `docs/` | Submission notes, product feedback, friction log |

## License
MIT
