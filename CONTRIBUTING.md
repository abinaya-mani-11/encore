# Contributing

- `main` must always run. No direct commits; open a PR from a branch named `core/...`, `gen/...` or `web/...`.
- One teammate reviews and approves. Squash merge.
- Run `python tests/test_core.py` before pushing.
- Never commit secrets. `.env` is ignored; put variable names only in `.env.example`.
- Commit messages: short and imperative, e.g. "Add grade_card validation".
- Contracts in ARCHITECTURE.md change only after the team agrees.
- Link each PR to its issue ("Closes #12") so the board stays current.
