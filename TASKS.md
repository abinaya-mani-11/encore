# Tasks and split

Deadline: **Oct 23, 2026, 12:00 pm PT** (Oct 24, 12:30 am IST). Feature freeze **Oct 20**, then demo and submission only.
Create one GitHub Issue per item below, labelled `core`, `gen` or `web`. One PR per issue.

Issues: https://github.com/g-s-jithesh/encore/issues

## Core, 40% (Jithesh, @g-s-jithesh): MCP server, state, integration
- [x] Scaffold: `srs.py`, `db.py`, `server.py`, `tests/test_core.py`
- [ ] Input validation and error messages that sound right when spoken
- [ ] `list_materials` / `delete_material` tools, if the demo needs them
- [ ] Integration test: an MCP client calls every tool against the running server
- [ ] Review and merge PRs, keep `main` green
- [ ] Own the Devpost submission form and the repo settings (private now, make public with MIT around **Oct 16**)

## Mano (@Mkkumar2006), 30%: AI generation + AWS
- [ ] `generate.make_cards` with Amazon Bedrock (boto3 Converse), JSON output, 5-10 cards per input
- [ ] Long input (chunking) and malformed model output (retry once, then fall back)
- [ ] Unit test with a mocked Bedrock client
- [ ] AWS/Bedrock rows in `docs/FEEDBACK.md`
- [ ] Stretch: import a PDF or transcript file into `add_material`

## Bee (@abinaya-mani-11), 30%: Alexa+ simulator + demo
- [ ] `web/app.py`: agent loop. List tools from the MCP server, call Bedrock Converse with tool use, run tool calls through an MCP client
- [ ] `web/index.html`: voice UI (Web Speech API speech-to-text and text-to-speech), Alexa-style look, text fallback
- [ ] End-to-end by voice: add notes, quiz, grade, progress
- [ ] Record the demo video using the script in `docs/SUBMISSION.md`
- [ ] Stretch: MCP App flashcard view (`ui://` resource) using the `create-mcp-app` / `add-app-to-server` skills

## Everyone
- [ ] Log friction as it happens in `docs/FEEDBACK.md` (up to +10% judging bonus)
- [ ] Test the README run steps from a clean clone before submitting

## Private-repo collaborators (add at submission time, invites expire in 7 days)
chris-trag, knmeiss, giolaq, anishamalde, mosesroth, emersonsklar, plus share with testing@devpost.com
