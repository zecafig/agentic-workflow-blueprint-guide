# Blueprint Used on Creation

## Required Preparation

- Before starting, update the `agentic-workflow-blueprint` repository.
- Review official blueprint files in `agentic-workflow-blueprint`.
- Review the official AWB skills catalog and select the skills relevant to the project.
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

## Official Workflow and Skill Naming Snapshot

- workflows: `document`, `review`, `changelog`, `linear`, `mcp-linear-planner`, `mcp-linear-sync`, `plan-to-blueprint`
- skills: record the official skill names or directories selected for this project
- runbooks: `document-review-changelog.md`, `linear-mcp.md`, `mcp-linear-sync.md`, `plan-to-blueprint.md`
- additional workflows observed upstream: `analyzing-kubernetes-audit-logs`, `brainstorming`, `c4-architecture`, `changelog-generator`, `html-manual`, `iac`, `implementing-devsecops-security-scanning`, `implementing-network-policies-for-kubernetes`, `implementing-pod-security-admission-controller`, `implementing-rbac-hardening-for-kubernetes`, `implementing-syslog-centralization-with-rsyslog`, `infra-operations`, `network-engineering`, `os-platform`, `performing-container-image-hardening`, `performing-container-security-scanning-with-trivy`, `performing-kubernetes-cis-benchmark-with-kube-bench`, `performing-vulnerability-scanning-with-nessus`, `plan-writing`, `radioactive`, `remediating-s3-bucket-misconfiguration`, `remotion-video-motion`, `scanning-containers-with-trivy-in-cicd`, `scanning-docker-images-with-trivy`, `scanning-kubernetes-manifests-with-kubesec`, `securing-aws-iam-permissions`, `securing-container-registry-images`, `securing-github-actions-workflows`, `securing-kubernetes-on-cloud`, `thermo-fix`, `thermo-nuclear-code-quality-review`, `triaging-vulnerabilities-with-ssvc-framework`, `ui-ux-pro-max`
- additional runbooks observed upstream: `iac-delivery.md`, `network-change.md`, `os-hardening-patching.md`

If official naming/contracts change, this snapshot must be updated.

## Migration Checklist to New Repo

- Copy files created during the initial inputs phase.
- Copy the required workflow files generated or selected from the blueprint flow.
- Record the selected skills in the new repo alongside workflow files and runbooks.
- Ensure orchestration files are present in the new repo.
- Add project tooling files as needed by the chosen stack (post-handoff).
- Keep this file in the new repo root for traceability.

## Handoff Acknowledgement

Confirm each item:

- Initial inputs were reviewed and accepted.
- Initial artifacts were prepared.
- Project-specific implementation now continues only in the new repo.
- Official `agentic-workflow-blueprint` repository remains unchanged by project-specific work.
