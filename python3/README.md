# Python 3 Bootstrap Layer

This folder contains all Python 3 files used by the guide bootstrap flow.

Assumption for this README: you are running commands from inside `python3/`.

## Files

- `guide_me.py`: interactive bootstrap input collector and optional copy assistant.
- `helpers.py`: shared constants and helper functions used by `guide_me.py`.
- `tests/`: pytest suite for Python 3 modules (coverage target: 100% for touched modules).
- `requirements.txt`: Python dependencies for this folder (user is moving this file here).

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 guide_me.py
```

The first prompt selects the project mode: `new` (bootstrap a brand new repository) or `existing` (apply this guide's docs/workflow files to a repository that already exists). Existing-project mode never overwrites files already present in the target repository and requires the target directory to already exist before copying. It also scans the target directory (one level deep) for existing context files (README, docs, manifests) and writes `bootstrap/PROJECT_CONTEXT.md` as an index of what it found; `AGENTS.md` is only added when no root instruction file (matching `existingRootDoc`, `AGENTS.md`, or `CLAUDE.md`) already exists in the target.

## Tests

```bash
pytest tests --cov=. --cov-report=term-missing
```

## Notes

- Generated blueprint outputs are written under `../generated_blueprints/`.
- Keep this folder Python-only and avoid mixing guide-core markdown files here.
- Developers are responsible for Python runtime decisions: virtual environments, dependencies, test and coverage strategy, automation, database integrations, and backend/frontend implementation details.
- AI in this guide supports bootstrap guidance and artifact preparation; it does not replace developer ownership of implementation choices.
- GitHub Actions policy: set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` at workflow level to avoid deprecated Node runtimes in JavaScript-based actions.
- CI trigger policy: run CI on `push` to `main` and on `pull_request` so every commit to main and every PR update is validated.
- Badge policy: use dynamic badges only (for example, workflow status and Codecov). Do not use static hardcoded result badges.
