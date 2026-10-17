# Encore

A voice study coach for Alexa+. Tell it what you studied, it builds flashcards, then
quizzes you by voice on a spaced schedule that it remembers across sessions.

Built for the Amazon Developer Hackathon (Alexa+ track). Design: [ARCHITECTURE.md](ARCHITECTURE.md).
Work split: [TASKS.md](TASKS.md). Workflow: [CONTRIBUTING.md](CONTRIBUTING.md).

## Run
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp; then fill in an LLM (below)
```
In `.env`, set `GEMINI_API_KEY` (a free key from [Google AI Studio](https://aistudio.google.com)).
That's the only key needed. Encore also has an Amazon Bedrock path (`LLM_PROVIDER=bedrock`,
AWS keys and `BEDROCK_MODEL_ID`), but we couldn't run it live: our new AWS account was never
cleared for Bedrock (see `docs/FEEDBACK.md`), so it's covered only by mocked tests.

Start both processes, each in its own terminal:
```bash
python server.py                 # MCP server at http://127.0.0.1:8000/mcp
python -m web.app                # voice app at http://127.0.0.1:5000
```
`ENCORE_PORT` changes the MCP server port (default 8000).

## Test
```bash
python tests/test_core.py                    # unit tests, prints "ok"
python tests/test_integration.py             # starts the server, calls every tool over HTTP
python tests/test_web.py                     # agent loop with mocked model + MCP
python -m unittest tests/test_generate.py    # card generation with a mocked Bedrock client
npm ci && npx playwright install chromium && npm run test:e2e   # browser voice flow
```
No test calls a real model. `LLM_PROVIDER=none` also runs card generation offline
(cards come from `question? answer` lines); the web agent still needs a model.

The flashcard MCP App HTML is included in the repository. To rebuild it after
changing `mcp_apps/flashcards.ts`, use Node.js 20+: `npm ci && npm run build:mcp-app`.

## Layout
| Path | What |
|---|---|
| `server.py` | MCP server and tools |
| `db.py`, `srs.py` | Card storage and spaced repetition |
| `generate.py` | Notes to flashcards (Gemini, optional Bedrock); chunking + retry |
| `gemini.py` | Minimal Gemini REST client (stdlib only) |
| `ingest.py` | Extract text from PDF / VTT / SRT / plain-text files |
| `web/` | Simulated Alexa+ voice client |
| `mcp_apps/` | MCP Apps flashcard UI source and bundled resource |
| `docs/` | Submission notes, product feedback, friction log |

## License
MIT
