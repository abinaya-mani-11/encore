# web/ (Teammate B)

Simulated Alexa+ client. See TASKS.md, section "Teammate B".

- `app.py`: agent loop. Connect to `http://127.0.0.1:8000/mcp` with an MCP client, list tools, call Bedrock Converse with those tools, run the tool calls, return the reply text.
- `index.html`: push-to-talk, Web Speech API for speech-to-text and text-to-speech, transcript view, text input fallback.
