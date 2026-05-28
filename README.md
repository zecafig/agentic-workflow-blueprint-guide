# agentic-workflow-blueprint-guide

[![CI](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/zecafig/agentic-workflow-blueprint-guide/graph/badge.svg?branch=main)](https://codecov.io/gh/zecafig/agentic-workflow-blueprint-guide)

This repository contains reusable guidance for starting new projects with the official `agentic-workflow-blueprint` (AWB). AWB is the source of truth for workflow contracts, structure, and runbooks. This guide is the bootstrap layer that validates inputs, verifies alignment, and moves required AWB artifacts into a new project repository.

Official AWB source:
- Name: `agentic-workflow-blueprint`
- Repository: `https://github.com/devton/agentic-workflow-blueprint`

## Scope

- Keep process guidance here in markdown.
- Keep this guide Python 3 bootstrap-only.
- Keep project implementation out of this repository.
- Keep the official blueprint repository free of project-specific changes.
- Keep workflow names and contract expectations aligned with official AWB.

## Files

- agentic_workflow_blueprint_guidance.md: canonical operating guide.
- blue_print_used_on_creation.md: template copied into each new project repository.
- bootstrap_checklist.md: run-by-run verification checklist for blueprint bootstrap and handoff.
- python3/guide_me.py: Python 3 CLI to collect blueprint inputs and generate starter output files.
- python3/helpers.py: shared Python 3 helper module for input, copy, and validation utilities.
- Makefile: standard team commands, including pre-bootstrap audit.
- README.md: scope and usage rules.

## Makefile Commands

Run these commands from the repository root.

- `make help`: list available targets.
- `make pre-bootstrap-audit`: run the mandatory pre-bootstrap alignment audit (`scripts/pre_bootstrap_audit.sh`).
- `make audit`: alias of `make pre-bootstrap-audit`.
- `make docs-audit`: run Python-only documentation consistency checks (`scripts/docs_audit.sh`).
- `make coverage`: run Python tests with a 100% coverage gate and write XML report to `python3/coverage.xml`.
- `make clean`: remove generated artifacts, logs, and Python cache directories, then recreate `generated_blueprints/`.

## Project Scope

- This repository supports only Python 3 bootstrap workflows.
- Command entrypoint: `python3 python3/guide_me.py`.
- No additional language bootstrap layers are planned in this repository.

## Official AWB Inventory Snapshot

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`

If upstream names/contracts change, update this guide repo before the next bootstrap run.

## How to use this repository

1. Update and review the official blueprint repository as source of truth.
2. Read `python3/README.md` before running anything.
3. Run the entrypoint: `python3 python3/guide_me.py`.
4. If the report shows `[FAIL]`/`[WARN]`, stop, fix those items, and rerun `python3 python3/guide_me.py` until the audit passes.
5. Open the target project repository in VS Code.
6. Review the generated input outputs from `python3/guide_me.py` and refine your answers by rerunning `python3 python3/guide_me.py` until the inputs are correct.
7. Treat the latest generated inputs (`projectSlug`, `workflowsWanted`, constraints, and stack details) as the source that feeds your AWB scaffolding decisions.
8. Complete `bootstrap_checklist.md` and treat unchecked required items as a hard stop.
9. Copy only selected blueprint artifacts into the target project repository and keep official AWB unchanged.
10. Start implementation only in the target project repository after the checklist and handoff gate are fully passed.
