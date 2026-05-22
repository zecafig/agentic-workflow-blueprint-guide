# Bootstrap Checklist

Use this checklist at the start of every new project to reduce setup drift.

## A. Preflight

- [ ] I pulled the latest changes from the official blueprint repository.
- [ ] I ran `make pre-bootstrap-audit` and it passed.
- [ ] I reviewed official AWB files and examples as source of truth.
- [ ] I opened the target project repository in VS Code.
- [ ] I reviewed blueprint changes and confirmed no project-specific changes will be made there.
- [ ] I reviewed guidance files in this repository.

## B. Input Capture

- [ ] I ran the available language entrypoint (`python3 python3/guide_me.py` currently).
- [ ] I reviewed generated input outputs and reran the language entrypoint to refine answers until inputs were correct.
- [ ] I confirmed the latest generated inputs are the source that will feed AWB scaffolding decisions.
- [ ] I reviewed and validated core constraints.
- [ ] I reviewed and validated stack-specific constraints.
- [ ] I confirmed workflowsWanted is correct.

## C. Handoff Gate

- [ ] Initial inputs were reviewed and accepted.
- [ ] Initial artifacts were generated or selected.
- [ ] I created or opened the new project repository.
- [ ] I copied only selected artifacts to the new project repository.
- [ ] I did not move or rewrite official blueprint files.

## D. New Repo Readiness

- [ ] blue_print_used_on_creation.md exists in the new project repository root.
- [ ] AGENTS.md and workflow files are present as needed.
- [ ] Workflow naming matches official AWB naming.
- [ ] Every workflow contract includes required sections: Goal, Scope, Triggers, Inputs, Invariants, Procedure, Outputs, Review gate, References.
- [ ] Root guidance stays minimal and links to canonical workflow contracts.

## E. Optional Project Runtime Validation (Post-Handoff)

- [ ] Tooling files are present (for example pyproject.toml, lint/test config, setup scripts).
- [ ] Paths and environment settings are configurable (no hard-coded critical paths).

## F. Optional First Validation Pass (Project-Specific)

- [ ] Setup/bootstrap command executed successfully in the new repo.
- [ ] Lint command executed successfully.
- [ ] Test command executed successfully.
- [ ] Coverage gates match project constraints.
- [ ] Next actions are documented for the first implementation task.

## Sign-off

- Project slug:
- Date:
- Prepared by:
- Approved by:
