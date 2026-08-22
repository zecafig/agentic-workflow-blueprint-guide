# Agentic Workflow Blueprint Guide

## Purpose

This guide explains how to start a project with agentic-workflow-blueprint, keep the official blueprint repository unchanged, and hand off implementation to the new project repository at the right time.

## Agent First-Read Verification Protocol

Any agent reading this repository for the first time must run this protocol before doing anything else. This section is the source of truth for how to verify the repository is healthy. Do not skip steps and do not assume a failure is harmless without independent proof.

1. **Run `make pre-bootstrap-audit` from the guide repo root.**
   - If it prints `Pre-bootstrap audit PASSED.`, continue to step 4.
   - If it prints `FAILED`, do not stop yet. Classify every `[FAIL]` line using step 2 or step 3.

2. **Failures about this guide repo's own files** (`README.md`, `agentic_workflow_blueprint_guidance.md`, `bootstrap_checklist.md`, `blue_print_used_on_creation.md`, `python3/guide_me.py`, `python3/helpers.py`, missing-section or forbidden-text checks, leftover generated files): treat these as real. Fix the content, rerun `make pre-bootstrap-audit`, and confirm it passes before continuing.

3. **Failures about the official `agentic-workflow-blueprint` sibling repo** (missing `AGENTS.md`/`SKILL.md`/`README.md`, missing `workflows`/`runbooks` directories, or "no upstream tracking branch configured"): do not accept the script's verdict at face value. Independently verify with direct, absolute-path commands before deciding whether this is real:
   - `ls -la <official-repo-path>/AGENTS.md <official-repo-path>/SKILL.md <official-repo-path>/README.md`
   - `git -C <official-repo-path> remote -v && git -C <official-repo-path> status -sb`
   - **Known environment artifact:** in a sandboxed terminal (for example, a VS Code chat agent tool sandbox), relative `..` traversal from the guide repo's working directory out to a sibling repository outside the current workspace folder can silently fail even though the files and git tracking genuinely exist. This shows up as `[FAIL] Missing file: .../guide/../agentic-workflow-blueprint/AGENTS.md` and `[FAIL] Official repo has no upstream tracking branch configured.` while direct `ls`/`git` checks on the same absolute path succeed.
   - If the direct checks show the files/tracking **do** exist, treat the audit failure as a sandbox/terminal artifact, not a repo defect. Re-run the audit from a normal (non-sandboxed) terminal, or re-run with the path pinned explicitly: `OFFICIAL_AWB_REPO=<absolute-path-to-official-repo> make pre-bootstrap-audit` (or the equivalent `bash scripts/pre_bootstrap_audit.sh` invocation). Only escalate to the user if it still fails after that.
   - If the direct checks confirm the files or tracking are genuinely missing, this is a real `[FAIL]`: stop, fix upstream alignment (pull/clone the official repo, configure the branch to track `origin/main`, or restore the missing files), and rerun until it passes.

4. **Run `make docs-audit`.** It must print `Documentation audit PASSED.` before continuing. This checks that Python-only scope statements, skills-catalog references, and forbidden multi-language phrasing stay consistent across `README.md`, `agentic_workflow_blueprint_guidance.md`, `bootstrap_checklist.md`, `python3/README.md`, and `python3/guide_me.py`.

5. **Run the Python 3 test suite with coverage** from `python3/`:
   ```bash
   cd python3
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pytest tests --cov=. --cov-report=term-missing
   ```
   Confirm all tests pass and coverage is 100% for `guide_me.py` and `helpers.py`. Equivalently, `make coverage` from the repo root enforces the same 100% gate and writes `python3/coverage.xml`.

6. **Only proceed** to the "Before Starting" steps below once:
   - Every real `[FAIL]` from `make pre-bootstrap-audit` is resolved (sandbox artifacts excluded per step 3).
   - `make docs-audit` passes.
   - The Python 3 test suite passes with 100% coverage.

If any step cannot be completed or verified, stop and report the specific unresolved failure instead of assuming success.

## Operating model

- The official `agentic-workflow-blueprint` repository is the source of workflow templates, skills, and contracts.
- This guidance repository is the source of the process rules you reuse on every project.
- The new project repository is where product implementation must happen.

Official AWB reference:

- Name: `agentic-workflow-blueprint`
- Repository: `https://github.com/devton/agentic-workflow-blueprint`

## Core Rule

Use the official `agentic-workflow-blueprint` repository as the source of truth, and execute project bootstrap in the target project repository.

## Responsibility Rule

Developers own language, stack, and implementation decisions.
AI is an assistant for guidance and scaffolding, not the decision-maker for runtime architecture.
Developers are responsible for virtual environments, dependency management, tests and coverage, automation/CI, database choices, and backend/frontend implementation.

## Boundary Rule

Do not make project-specific implementation changes in the official `agentic-workflow-blueprint` repository.

Use the official blueprint repository to:

- Inspect the current workflow structure.
- Review the latest blueprint files.
- Define the initial inputs for the new project.
- Prepare the initial files that will be copied into the new repository.

Do not use the official blueprint repository to:

- Hold the real implementation of the new product.
- Accumulate project-specific commits.
- Become the working repository for the new product.

Never copy this guidance repository into the official blueprint repository.

## Before Starting

Before starting a new project:

1. Update the local `agentic-workflow-blueprint` repository.
2. Run the mandatory automated pre-bootstrap audit in this guide repository:
	`make pre-bootstrap-audit`
3. Review official blueprint files and examples in `agentic-workflow-blueprint`.
4. Review the official skills catalog and identify which skills are relevant to this project.
5. Ask the LLM to review current changes in the blueprint repository and this guidance repository.
6. Open the target project repository in VS Code.
7. Define the project inputs before generating files.

## Initial Inputs

Define these inputs clearly before generating any new-project files:

- `projectSlug`
- `baseBranch`
- `techStack`
- `existingRootDoc`
- `workflowsWanted`
- `constraints`

Constraints must be written as objective pass/fail rules, not vague preferences.

## Initial Artifacts to Prepare

During the blueprint phase, prepare the initial artifacts that the new repository will need.

These typically include:

- Root instruction files such as `AGENTS.md`.
- Workflow contract files under `skills/<project>/...`.
- Selected skills or skill references from the official skills catalog, when they are needed for the project.
- Any other files created directly from the initial inputs.

Only copy selected artifacts into the new project repository. Do not move or rewrite official blueprint files.

Do not require implementation or runtime setup (lint, test, build tooling) as part of blueprint completion. Treat those as post-handoff project setup owned by the development team.

## Official Workflow, Skill, and Runbook Inventory

Track these official examples and keep naming aligned:

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- skills: review the official AWB skills catalog and capture the skill IDs or directories that match the project scope and selected workflows
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`
- additional workflows observed upstream: `analyzing-kubernetes-audit-logs`, `brainstorming`, `c4-architecture`, `changelog-generator`, `html-manual`, `iac`, `implementing-devsecops-security-scanning`, `implementing-network-policies-for-kubernetes`, `implementing-pod-security-admission-controller`, `implementing-rbac-hardening-for-kubernetes`, `implementing-syslog-centralization-with-rsyslog`, `infra-operations`, `network-engineering`, `os-platform`, `performing-container-image-hardening`, `performing-container-security-scanning-with-trivy`, `performing-kubernetes-cis-benchmark-with-kube-bench`, `performing-vulnerability-scanning-with-nessus`, `plan-writing`, `radioactive`, `remediating-s3-bucket-misconfiguration`, `remotion-video-motion`, `scanning-containers-with-trivy-in-cicd`, `scanning-docker-images-with-trivy`, `scanning-kubernetes-manifests-with-kubesec`, `securing-aws-iam-permissions`, `securing-container-registry-images`, `securing-github-actions-workflows`, `securing-kubernetes-on-cloud`, `thermo-fix`, `thermo-nuclear-code-quality-review`, `triaging-vulnerabilities-with-ssvc-framework`, `ui-ux-pro-max`
- additional runbooks observed upstream: `iac-delivery.md`, `network-change.md`, `os-hardening-patching.md`

If upstream naming or contracts change, update this guide before the next bootstrap.

## Required Workflow Contract Sections

Each workflow contract must include all required sections:

- `Goal`
- `Scope`
- `Triggers`
- `Inputs`
- `Invariants`
- `Procedure`
- `Outputs`
- `Review gate`
- `References`

## Handoff Moment

Continue from the new repository after both of these conditions are true:

1. The initial inputs have been reviewed and accepted.
2. The initial artifacts for the new project have been generated or selected.

At that point, create or open the new repository and move the prepared files there.

After handoff, do not continue implementation in the official blueprint repository.

## What Must Exist in the New Repository

The new repository must contain:

- The files created from the initial inputs.
- The workflow and orchestration files needed for the agent harness.
- Any project tooling files required by the target stack (post-handoff, project-specific).
- A project-local traceability file named `blue_print_used_on_creation.md`.

## Required Traceability File

Create a file named `blue_print_used_on_creation.md` in the new repository root.

Its purpose is to record:

- That the project was started from the blueprint flow.
- What preparation steps were required before start.
- That the official blueprint repository must remain unchanged for project-specific work.
- When the team should continue from the new repository.

Use the template in this guidance repository as the starting point.

## Recommended Execution Flow

1. Update the official `agentic-workflow-blueprint` repository.
2. Run `make pre-bootstrap-audit` and proceed only if it passes.
3. Review the current guidance in this repository and the official blueprint files.
4. Review the official skills catalog and capture the selected skills for the new project.
5. Open the target project repository in VS Code.
6. Define and validate the initial project inputs.
7. Prepare the initial artifacts for the new project.
8. Copy only the prepared initial-input files, selected workflow files, and relevant skill references into the target repository.
9. Add `blue_print_used_on_creation.md` to the target repository root.
10. Confirm handoff gate: implementation now continues only in the target repository.
11. Keep the official blueprint repository clean for future updates and review cycles.

## Maintenance Rule

Keep this guide in markdown and update it when the flow changes. Review it at the start of every new project.
