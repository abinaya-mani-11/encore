# web/ (Teammate B)

Simulated Alexa+ client. See TASKS.md, section "Teammate B".

- `app.py`: agent loop. Connect to `http://127.0.0.1:8000/mcp` with an MCP client, list tools, send them to the model (Gemini, or Bedrock Converse with `LLM_PROVIDER=bedrock`), run the tool calls, return the reply text.
- `index.html`: push-to-talk, Web Speech API for speech-to-text and text-to-speech, transcript view, text input fallback.

Run the MCP server and web host in separate terminals from the repository root:

```bash
python server.py
python -m web.app
```

Open `http://127.0.0.1:5000`. Set `GEMINI_API_KEY` (or the Bedrock settings with
`LLM_PROVIDER=bedrock`) in `.env` before starting both processes.
