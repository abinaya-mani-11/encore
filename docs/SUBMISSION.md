# Submission notes

**Name:** Encore
**Pitch:** Tell Alexa+ what you studied today. Encore turns it into flashcards and quizzes you by voice on a spaced schedule, picking up where you left off every session.
**Problem:** Students forget most of what they hear within days, and nobody has time to turn notes into review material.
**Track:** Alexa+ (simulated Alexa+ experience + self-hosted MCP server). **Mini challenges:** AWS Builder, Open Source.

## Text description
**Inspiration.** Students forget most of a lecture within days. Spaced repetition fixes that, but making flashcards takes time nobody has. With Alexa+ you can just say what you learned.

**What it does.** Tell Encore what you studied, by speaking or pasting notes. Encore turns it into flashcards, then quizzes you by voice: it asks a question, you answer out loud, it judges your answer and tells you when that card comes back. Browser speech recognition turns speech into text, and speech synthesis reads Encore's replies aloud; typed input remains available. Cards you miss return tomorrow; cards you know return in 3, 7, then 14 days. Progress persists, so every session picks up where the last one ended. You can quiz one topic ("quiz me on photosynthesis"), list topics, view cards in an interactive MCP App, and delete them.

**How we built it.** A self-hosted MCP server (Python, official MCP SDK 2.x, Streamable HTTP, spec 2025-11-25) exposes tools for adding notes, reviewing and grading cards, checking progress, listing and deleting topics, and viewing saved flashcards. State lives in SQLite with a Leitner spaced-repetition schedule. Amazon Bedrock generates flashcards. A web app simulates Alexa+: browser speech recognition and synthesis, plus a Bedrock agent loop that connects to the server as an MCP client and calls the tools. The flashcard view is served as a `ui://` MCP App resource, with a text response for clients that do not support Apps.

**Challenges.** The MCP Python SDK's v2 APIs differ from many older examples, so the server and its MCP Apps extension had to be integrated against the installed SDK rather than copying legacy `FastMCP` patterns. The browser also needs separate fallbacks for speech recognition, speech synthesis, and typed input.
**Accomplishments.** Encore has a browser-based voice/text simulator, a Bedrock-powered MCP tool-calling loop, persistent spaced-repetition state, and an interactive flashcard view registered as an MCP App.
**What we learned.** MCP tool results can serve both conversational clients and richer app views: a spoken text result keeps the tool useful without UI support, while structured content feeds the flashcard app. Speech input and output are independent browser capabilities, so the text experience remains important.
**What's next.** Real Alexa+ integration, importing lecture recordings and PDFs, and shared decks for study groups.

## Demo video script (under 3:00, best part first)
- 0:00-0:20 Problem, then "Encore: a voice study coach for Alexa+"
- 0:20-1:00 Speak your notes, flashcards get created (Bedrock)
- 1:00-2:00 Voice quiz: question, spoken answer, graded, next card
- 2:00-2:30 Next session: progress and schedule persisted
- 2:30-2:45 Open the interactive MCP App flashcard view
- 2:45-3:00 Architecture in one shot (MCP server over Streamable HTTP, Bedrock), impact

## Checklist
- [x] Text description: features and how it works
- [ ] Repo public with MIT visible in About, or private and shared with testing@devpost.com + the Amazon team (see TASKS.md)
- [ ] Setup and run instructions work from a clean clone
- [ ] Simulator source is in the repo; MCP server (spec 2025-11-25, Streamable HTTP) shown running
- [ ] Demo video: YouTube or Vimeo, public, under 3 minutes, English, no copyrighted music
- [ ] Product feedback for every tool used (see FEEDBACK.md)
- [ ] AWS Builder: describe Bedrock usage in the feedback answer
- [ ] Open Source: contribution URL, repo URL, GitHub username, what/how/why
- [ ] Optional: feature requests and friction log
