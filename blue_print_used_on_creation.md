# Blueprint Used on Creation

## Required Preparation

- Before starting, update the `agentic-workflow-blueprint` repository.
- Review official blueprint files in `agentic-workflow-blueprint`.
- Open the target project repository in VS Code.
- Ask the LLM to review current blueprint changes and this guidance repository.

## Initial Input Snapshot

Record the values used for:

- `projectSlug`
- `baseBranch`
- `techStack`
- `existingRootDoc`
- `workflowsWanted`
- `constraints`

## Boundary Rules

- Use the official `agentic-workflow-blueprint` repository as the source of truth for structure and contracts.
- Execute scaffolding and implementation in the target project repository.
- Do not modify the official `agentic-workflow-blueprint` repository with project-specific implementation changes.
- Continue implementation from the new repository only after initial inputs are validated and initial artifacts are prepared.

## Official Workflow Naming Snapshot

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`

If official naming/contracts change, this snapshot must be updated.

## Migration Checklist to New Repo

- Copy files created during the initial inputs phase.
- Copy the required workflow files generated or selected from the blueprint flow.
- Ensure orchestration files are present in the new repo.
- Add project tooling files as needed by the chosen stack (post-handoff).
- Keep this file in the new repo root for traceability.

## Handoff Acknowledgement

Confirm each item:

- Initial inputs were reviewed and accepted.
- Initial artifacts were prepared.
- Project-specific implementation now continues only in the new repo.
- Official `agentic-workflow-blueprint` repository remains unchanged by project-specific work.
