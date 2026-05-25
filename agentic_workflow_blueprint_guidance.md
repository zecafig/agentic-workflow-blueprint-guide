# Agentic Workflow Blueprint Guide

## Purpose

This guide defines how to start a project with agentic-workflow-blueprint, keep the official blueprint repository unchanged, and hand off implementation to the new project repository at the right time.

## Operating model

- The official `agentic-workflow-blueprint` repository is the source of workflow templates and contracts.
- This guidance repository is the source of the process rules you reuse on every project.
- The new project repository is where product implementation must happen.

Official AWB reference:

- Name: `agentic-workflow-blueprint`
- Repository: `https://github.com/devton/agentic-workflow-blueprint`

## Core Rule

Use the official `agentic-workflow-blueprint` repository as the source of truth.
Execute project bootstrap in the target project repository.

## Boundary Rule

Do not make project-specific implementation changes in the official `agentic-workflow-blueprint` repository.

Use the official blueprint repository to:

- inspect the current workflow structure
- review the latest blueprint files
- define the initial inputs for the new project
- prepare the initial files that will be copied into the new repository

Do not use the official blueprint repository to:

- hold the real implementation of the new product
- accumulate project-specific commits
- become the working repository for the new product

Never copy this guidance repository into the official blueprint repository.

## Before Starting

Before starting a new project:

1. Update the local `agentic-workflow-blueprint` repository.
2. Run the mandatory automated pre-bootstrap audit in this guide repository:
	`make pre-bootstrap-audit`
3. Review official blueprint files and examples in `agentic-workflow-blueprint`.
4. Ask the LLM to review the current changes in the blueprint repo and review this guide repository.
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

- root instruction files such as `AGENTS.md`
- workflow contract files under `skills/<project>/...`
- any other files created directly from the initial inputs

Only copy selected artifacts into the new project repository. Do not move or rewrite official blueprint files.

Do not require implementation/runtime setup (lint/test/build tooling) as part of blueprint completion. Treat those as post-handoff project setup.

## Official Workflow and Runbook Inventory

Track these official examples and keep naming aligned:

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`

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

- the files created from the initial inputs
- the workflow and orchestration files needed for the agent harness
- any project tooling files required by the target stack (post-handoff, project-specific)
- a project-local traceability file named `blue_print_used_on_creation.md`

## Required Traceability File

Create a file named `blue_print_used_on_creation.md` in the new repository root.

Its purpose is to record:

- that the project was started from the blueprint flow
- what preparation steps were required before start
- that the official blueprint repository must remain unchanged for project-specific work
- when the team should continue from the new repository

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
