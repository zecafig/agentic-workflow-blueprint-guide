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

## Tests

```bash
pytest tests --cov=. --cov-report=term-missing
```

## Notes

- Generated blueprint outputs are written under `../generated_blueprints/`.
- Keep this folder language-specific and avoid mixing guide-core markdown files here.
- GitHub Actions policy: set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` at workflow level to avoid deprecated Node runtimes in JavaScript-based actions.
- CI trigger policy: run CI on `push` to `main` and on `pull_request` so every commit to main and every PR update is validated.
- Badge policy: use dynamic badges only (for example, workflow status and Codecov). Do not use static hardcoded result badges.
