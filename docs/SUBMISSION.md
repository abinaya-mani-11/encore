# Submission notes

**Name:** Recall
**Pitch:** Tell Alexa+ what you studied today. Recall turns it into flashcards and quizzes you by voice on a spaced schedule, picking up where you left off every session.
**Problem:** Students forget most of what they hear within days, and nobody has time to turn notes into review material.
**Track:** Alexa+ (simulated Alexa+ experience + self-hosted MCP server). **Mini challenges:** AWS Builder, Open Source.

## Demo video script (under 3:00, best part first)
- 0:00-0:20 Problem, then "Recall: a voice study coach for Alexa+"
- 0:20-1:00 Speak your notes, flashcards get created (Bedrock)
- 1:00-2:00 Voice quiz: question, spoken answer, graded, next card
- 2:00-2:30 Next session: progress and schedule persisted
- 2:30-3:00 Architecture in one shot (MCP server over Streamable HTTP, Bedrock), impact

## Checklist
- [ ] Text description: features and how it works
- [ ] Repo public with MIT visible in About, or private and shared with testing@devpost.com + the Amazon team (see TASKS.md)
- [ ] Setup and run instructions work from a clean clone
- [ ] Simulator source is in the repo; MCP server (spec 2025-11-25, Streamable HTTP) shown running
- [ ] Demo video: YouTube or Vimeo, public, under 3 minutes, English, no copyrighted music
- [ ] Product feedback for every tool used (see FEEDBACK.md)
- [ ] AWS Builder: describe Bedrock usage in the feedback answer
- [ ] Open Source: contribution URL, repo URL, GitHub username, what/how/why
- [ ] Optional: feature requests and friction log
