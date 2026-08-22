# agentic-workflow-blueprint-guide

[![CI](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/zecafig/agentic-workflow-blueprint-guide/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/zecafig/agentic-workflow-blueprint-guide/graph/badge.svg?branch=main)](https://codecov.io/gh/zecafig/agentic-workflow-blueprint-guide)

This repository contains reusable guidance for starting new projects with the official `agentic-workflow-blueprint` (AWB). AWB is the source of truth for workflow contracts, structure, runbooks, and the official skills catalog. This guide is the bootstrap layer that validates inputs, verifies alignment, and moves required AWB artifacts into a new project repository.

Official AWB source:
- Name: `agentic-workflow-blueprint`
- Repository: `https://github.com/devton/agentic-workflow-blueprint`

## Scope

- Keep process guidance here in markdown.
- Keep this guide Python 3 bootstrap-only.
- Keep project implementation out of this repository.
- Keep the official blueprint repository free of project-specific changes.
- Keep workflow names and contract expectations aligned with official AWB.
- Keep the official AWB skills catalog in view when selecting project capabilities.

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

## Responsibility Model

- Python developers define and own implementation decisions.
- AI supports documentation, input collection, and scaffolding guidance in this repository.
- Developers, not AI, decide and execute virtual environment setup, dependency selection (`pip`), test and coverage standards, automation/CI flows, database architecture, and backend/frontend implementation choices.

## Official AWB Inventory Snapshot

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- skills: review the official AWB skills catalog and capture the skill IDs or directories that match the project scope and selected workflows
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`
- additional workflows observed upstream: `analyzing-kubernetes-audit-logs`, `brainstorming`, `c4-architecture`, `changelog-generator`, `html-manual`, `iac`, `implementing-devsecops-security-scanning`, `implementing-network-policies-for-kubernetes`, `implementing-pod-security-admission-controller`, `implementing-rbac-hardening-for-kubernetes`, `implementing-syslog-centralization-with-rsyslog`, `infra-operations`, `network-engineering`, `os-platform`, `performing-container-image-hardening`, `performing-container-security-scanning-with-trivy`, `performing-kubernetes-cis-benchmark-with-kube-bench`, `performing-vulnerability-scanning-with-nessus`, `plan-writing`, `radioactive`, `remediating-s3-bucket-misconfiguration`, `remotion-video-motion`, `scanning-containers-with-trivy-in-cicd`, `scanning-docker-images-with-trivy`, `scanning-kubernetes-manifests-with-kubesec`, `securing-aws-iam-permissions`, `securing-container-registry-images`, `securing-github-actions-workflows`, `securing-kubernetes-on-cloud`, `thermo-fix`, `thermo-nuclear-code-quality-review`, `triaging-vulnerabilities-with-ssvc-framework`, `ui-ux-pro-max`
- additional runbooks observed upstream: `iac-delivery.md`, `network-change.md`, `os-hardening-patching.md`

If upstream names/contracts change, update this guide repo before the next bootstrap run.

## Agent First-Read Verification Protocol

Any agent must run the full protocol in `agentic_workflow_blueprint_guidance.md` ("Agent First-Read Verification Protocol") before starting bootstrap work: run `make pre-bootstrap-audit`, `make docs-audit`, and the Python 3 test suite with coverage, and confirm all real failures are resolved. That section also documents a known sandboxed-terminal artifact where checks against the official `agentic-workflow-blueprint` sibling repo can report false failures; verify with direct `ls`/`git` commands before treating any such failure as real.

## How to use this repository

1. Update and review the official blueprint repository as source of truth.
2. Read `python3/README.md` before running anything.
3. Run the entrypoint: `python3 python3/guide_me.py`.
4. If the report shows `[FAIL]`/`[WARN]`, stop, fix those items, and rerun `python3 python3/guide_me.py` until the audit passes.
5. Open the target project repository in VS Code.
6. Review the generated input outputs from `python3/guide_me.py` and refine your answers by rerunning `python3 python3/guide_me.py` until the inputs are correct.
7. Treat the latest generated inputs (`projectSlug`, `workflowsWanted`, constraints, and stack details) as source material for developer-led AWB scaffolding decisions.
8. Complete `bootstrap_checklist.md` and treat unchecked required items as a hard stop.
9. Copy only selected blueprint artifacts into the target project repository and keep official AWB unchanged.
10. Start implementation only in the target project repository after the checklist and handoff gate are fully passed.
