# Agentic Workflow Blueprint Guide

## Purpose

This guide explains how to start a project with agentic-workflow-blueprint, keep the official blueprint repository unchanged, and hand off implementation to the new project repository at the right time.

## Operating model

- The official `agentic-workflow-blueprint` repository is the source of workflow templates and contracts.
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
4. Ask the LLM to review current changes in the blueprint repository and this guidance repository.
5. Open the target project repository in VS Code.
6. Define the project inputs before generating files.

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
- Any other files created directly from the initial inputs.

Only copy selected artifacts into the new project repository. Do not move or rewrite official blueprint files.

Do not require implementation or runtime setup (lint, test, build tooling) as part of blueprint completion. Treat those as post-handoff project setup owned by the development team.

## Official Workflow and Runbook Inventory

Track these official examples and keep naming aligned:

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
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
4. Open the target project repository in VS Code.
5. Define and validate the initial project inputs.
6. Prepare the initial artifacts for the new project.
7. Copy only the prepared initial-input files and selected workflow files into the target repository.
8. Add `blue_print_used_on_creation.md` to the target repository root.
9. Confirm handoff gate: implementation now continues only in the target repository.
10. Keep the official blueprint repository clean for future updates and review cycles.

## Maintenance Rule

Keep this guide in markdown and update it when the flow changes. Review it at the start of every new project.
