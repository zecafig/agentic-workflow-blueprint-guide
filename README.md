# agentic-workflow-blueprint-guide

[![CI](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml)
[![Coverage Gate](https://img.shields.io/github/actions/workflow/status/zecafig/agentic-workflow-blueprint-guide/ci.yml?branch=main&label=coverage%20gate)](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml)

This repository contains reusable guidance for starting new projects with the official `agentic-workflow-blueprint` (AWB), which is the source of truth for workflow contracts, structure, and runbooks; this guide acts as the bootstrap layer that validates inputs, verifies alignment, and moves required AWB artifacts into a new project repository.

Official AWB source:
- Name: `agentic-workflow-blueprint`
- Repository: `https://github.com/devton/agentic-workflow-blueprint`

## Scope

- Keep process guidance here in markdown.
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

## Language Support

- Planned: Other language-specific bootstrap files.
- Current validated path: Python 3 (`python3/guide_me.py`).

## Official AWB Inventory Snapshot

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`

If upstream names/contracts change, update this guide repo before the next bootstrap run.

## How to use this repository

1. Update and review the official blueprint repository as source of truth.
2. Choose your project language/stack profile.
3. Enter the language directory and read its local README before running anything:
	- Python 3: `python3/README.md`
4. Run the available language entrypoint:
	- Python 3 (currently available): `python3 python3/guide_me.py`
	- Other languages: planned (not available yet in this repository)
5. If the report shows `[FAIL]`/`[WARN]`, stop, fix those items, and rerun `python3 python3/guide_me.py` until the audit passes.
6. Open the target project repository in VS Code.
7. Review the generated input outputs from `python3/guide_me.py` and refine your answers by rerunning `python3 python3/guide_me.py` until the inputs are correct.
8. Treat the latest generated inputs (`projectSlug`, `workflowsWanted`, constraints, and stack details) as the source that feeds your AWB scaffolding decisions.
9. Complete `bootstrap_checklist.md` and treat unchecked required items as a hard stop.
10. Copy only selected blueprint artifacts into the target project repository and keep official AWB unchanged.
11. Start implementation only in the target project repository after the checklist and handoff gate are fully passed.
