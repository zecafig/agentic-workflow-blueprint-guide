#!/usr/bin/env python3
"""Interactive helper to collect blueprint inputs for a new project.

This script guides a developer through the initial parameters used by the
agentic-workflow-blueprint flow and writes both JSON and Markdown outputs.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import List

from helpers import (
    BlueprintInputs,
    DEFAULT_CORE_RULES,
    DEFAULT_STACK_SPECIFIC_RULES,
    DEFAULT_WORKFLOWS,
    GENERATED_BLUEPRINTS_DIR,
    KNOWN_WORKFLOWS,
    copy_bootstrap_assets,
    extract_audit_findings,
    prompt,
    prompt_csv_list,
    prompt_multiline,
    prompt_yes_no,
    recommended_runbooks,
    unique_in_order,
    validate_slug,
)


def print_input_guidance() -> None:
    print("Input guidance (what you are about to provide):")
    print("- Official AWB: agentic-workflow-blueprint")
    print("- Official AWB repo: https://github.com/devton/agentic-workflow-blueprint")
    print("- projectSlug: short repo identifier in kebab-case (example: billing-api)")
    print("- baseBranch: integration branch name (example: main or develop)")
    print("- existingRootDoc: root instruction file used by the project (example: AGENTS.md)")
    print("- workflowsWanted: comma-separated workflow ids (example: document, review, changelog)")
    print("- known workflows: document, review, changelog, linear, mcp-linear-planner, mcp-linear-sync")
    print("- techStack: one item per line (example: Python, FastAPI, PostgreSQL)")
    print("- core rules: cross-project hard constraints")
    print("- stack-specific rules: implementation constraints tied to your chosen stack")
    print("- stack-specific defaults are preloaded for Python 3, with option to replace")
    print()


def to_markdown(data: BlueprintInputs) -> str:
    def bullet(lines: List[str]) -> str:
        return "\n".join(f"- {line}" for line in lines)

    workflow_list = ", ".join(data.workflows_wanted)
    runbook_list = ", ".join(recommended_runbooks(data.workflows_wanted))

    return "\n".join(
        [
            f"# Blueprint Inputs: {data.project_slug}",
            "",
            "## Metadata",
            f"- Collected at (UTC): {data.collected_at_utc}",
            "",
            "## Required Inputs",
            f"- projectSlug: {data.project_slug}",
            f"- baseBranch: {data.base_branch}",
            f"- existingRootDoc: {data.existing_root_doc}",
            f"- workflowsWanted: {', '.join(data.workflows_wanted)}",
            "",
            "## Tech Stack",
            bullet(data.tech_stack) or "- (none)",
            "",
            "## Constraints",
            "### Core Rules",
            bullet(data.core_rules) or "- (none)",
            "",
            "### Stack-Specific Rules",
            bullet(data.stack_specific_rules) or "- (none)",
            "",
            "### Canonical Constraints",
            bullet(data.core_rules + data.stack_specific_rules) or "- (none)",
            "",
            "## Notes",
            bullet(data.notes) if data.notes else "- (none)",
            "",
            "## Next Actions",
            "1. Create/open your target project repository directory and switch to it.",
            "2. Create `bootstrap/inputs/` in the target repo and move the generated input JSON/Markdown snapshots there.",
            "3. Keep `blue_print_used_on_creation.md` at the target repository root.",
            f"4. Copy selected workflow folders from official AWB: {workflow_list}.",
            f"5. Copy related runbooks from official AWB: {runbook_list or '(none selected)'}.",
            "6. Copy `AGENTS.md` from official AWB as a starting point, then adapt it for the target project.",
            "7. Run your normal project setup/validation in the target repo and begin implementation there only.",
            "",
        ]
    )


def to_creation_template(data: BlueprintInputs) -> str:
    workflow_list = ", ".join(data.workflows_wanted)
    runbooks = recommended_runbooks(data.workflows_wanted)

    return "\n".join(
        [
            "# Blueprint Used on Creation",
            "",
            "Official AWB source: `https://github.com/devton/agentic-workflow-blueprint`",
            "",
            "## Required Preparation",
            "",
            "- Before start, update `agentic-workflow-blueprint` repo.",
            "- Run `make pre-bootstrap-audit` in this guide repository and proceed only if it passes.",
            "- Review official blueprint files in `agentic-workflow-blueprint`.",
            "- Open the target project repository in VS Code.",
            "- Ask the LLM to review the current blueprint changes and this guidance repo.",
            "",
            "## Initial Input Snapshot",
            "",
            f"- `projectSlug`: {data.project_slug}",
            f"- `baseBranch`: {data.base_branch}",
            f"- `existingRootDoc`: {data.existing_root_doc}",
            f"- `workflowsWanted`: {workflow_list}",
            "",
            "### techStack",
            *[f"- {item}" for item in data.tech_stack],
            "",
            "### constraints (core rules)",
            *[f"- {item}" for item in data.core_rules],
            "",
            "### constraints (stack-specific rules)",
            *[f"- {item}" for item in data.stack_specific_rules],
            "",
            "### constraints (canonical)",
            *[f"- {item}" for item in (data.core_rules + data.stack_specific_rules)],
            "",
            "## Boundary Rules",
            "",
            "- Use official `agentic-workflow-blueprint` as source of truth for workflow structure and contracts.",
            "- Execute scaffolding and implementation in the target project repository.",
            "- Do not modify the official `agentic-workflow-blueprint` repository with project-specific implementation changes.",
            "- Continue implementation from the new repository only after initial inputs are validated and initial artifacts are prepared.",
            "",
            "## Migration Checklist to New Repo",
            "",
            "- Create/open the target project repository directory.",
            "- Move generated input snapshot files (`blueprint_inputs_*.json` and `blueprint_inputs_*.md`) into `bootstrap/inputs/` in the target repo.",
            "- Keep this file as `blue_print_used_on_creation.md` at the target repo root.",
            "- Copy files created during the initial inputs phase.",
            "- Copy the required workflow files generated or selected from the blueprint flow.",
            f"- Copy selected official workflow folders: {workflow_list}.",
            *[f"- Copy runbook from official AWB: {name}." for name in runbooks],
            "- Copy `AGENTS.md` from official AWB as a starting point and adapt it for the target project.",
            "- Ensure orchestration files are present in the new repo.",
            "- Add project tooling files as needed by the chosen stack (post-handoff).",
            "- Keep this file in the new repo root for traceability.",
            "",
            "## Handoff Acknowledgement",
            "",
            "- Initial inputs were reviewed and accepted.",
            "- Initial artifacts were prepared.",
            "- Project-specific implementation now continues only in the new repo.",
            "- Official `agentic-workflow-blueprint` repository remains unchanged by project-specific work.",
            "",
        ]
    )


def write_outputs(data: BlueprintInputs) -> tuple[Path, Path, Path]:
    guide_dir = Path(__file__).resolve().parent.parent
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = guide_dir / GENERATED_BLUEPRINTS_DIR / data.project_slug / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    stem = f"blueprint_inputs_{data.project_slug}_{timestamp}"

    json_path = run_dir / f"{stem}.json"
    md_path = run_dir / f"{stem}.md"
    creation_template_path = run_dir / "blue_print_used_on_creation.md"

    json_path.write_text(json.dumps(asdict(data), indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(data), encoding="utf-8")
    creation_template_path.write_text(to_creation_template(data), encoding="utf-8")

    return json_path, md_path, creation_template_path


def run_pre_bootstrap_audit() -> bool:
    guide_dir = Path(__file__).resolve().parent.parent
    cmd = ["make", "pre-bootstrap-audit"]

    print("Running mandatory pre-bootstrap audit...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=guide_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("Error: `make` command was not found in this environment.")
        print("Install make and rerun this script.")
        return False

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())

    if result.returncode != 0:
        findings = extract_audit_findings(f"{result.stdout}\n{result.stderr}")
        print()
        print("Pre-bootstrap audit failed.")
        if findings:
            print("Failure report:")
            for finding in findings:
                print(f"- {finding}")
        print("Fix the reported [FAIL]/[WARN] items and rerun guide_me.py.")
        return False

    print("Pre-bootstrap audit passed.")
    return True


def run() -> int:
    print("Agentic Workflow Blueprint - Input Collector")
    print("Run this while preparing a new project bootstrap.")
    print()

    if not run_pre_bootstrap_audit():
        return 1

    print()
    print_input_guidance()

    while True:
        try:
            project_slug = validate_slug(
                prompt("projectSlug (kebab-case, lowercase letters/digits/hyphens)", "my-project")
            )
            break
        except ValueError as exc:
            print(f"Error: {exc}")

    base_branch = prompt("baseBranch (integration branch)", "main")
    existing_root_doc = prompt("existingRootDoc (root instruction file)", "AGENTS.md")
    workflows_wanted = prompt_csv_list(
        "workflowsWanted (comma-separated workflow ids)", DEFAULT_WORKFLOWS
    )
    workflows_wanted = unique_in_order(workflows_wanted)
    unknown_workflows = [w for w in workflows_wanted if w not in KNOWN_WORKFLOWS]
    if unknown_workflows:
        print(
            "Warning: unknown workflow ids provided: "
            f"{', '.join(unknown_workflows)}"
        )
        print("They will be kept in inputs, but copy from official AWB may fail for them.")

    tech_stack = prompt_multiline(
        "Enter tech stack items (examples: Node.js, Python, PostgreSQL, Redis, React)."
    )

    use_default_core = prompt_yes_no("Use default core rules", default_yes=True)
    core_rules = (
        DEFAULT_CORE_RULES
        if use_default_core
        else prompt_multiline("Enter core rules", defaults=DEFAULT_CORE_RULES)
    )

    print("Included stack-specific rules (Python 3):")
    for rule in DEFAULT_STACK_SPECIFIC_RULES:
        print(f"- {rule}")

    use_default_stack_specific = prompt_yes_no(
        "Use these included stack-specific rules", default_yes=True
    )
    if use_default_stack_specific:
        stack_specific_rules = DEFAULT_STACK_SPECIFIC_RULES
    else:
        stack_specific_rules = prompt_multiline("Enter your own stack-specific rules")

    notes = prompt_multiline("Any extra notes", defaults=[])

    collected_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    data = BlueprintInputs(
        project_slug=project_slug,
        base_branch=base_branch,
        existing_root_doc=existing_root_doc,
        workflows_wanted=workflows_wanted,
        tech_stack=tech_stack,
        core_rules=core_rules,
        stack_specific_rules=stack_specific_rules,
        notes=notes,
        collected_at_utc=collected_at_utc,
    )

    json_path, md_path, creation_template_path = write_outputs(data)

    print()
    print("Done. Files created:")
    print(f"- {json_path}")
    print(f"- {md_path}")
    print(f"- {creation_template_path}")
    print("- (all files are written under generated_blueprints/)")
    print()
    print("What to do now (recommended):")
    print(f"1. Create/open target repo directory: ../{data.project_slug}")
    print("2. In target repo, create: bootstrap/inputs/")
    print(f"3. Move snapshots to target repo: {json_path.name}, {md_path.name}")
    print("4. Keep blue_print_used_on_creation.md in target repo root")
    print("5. Copy from official AWB repo:")
    print("   - AGENTS.md")
    print("   - selected workflow folders under workflows/")
    runbooks = recommended_runbooks(data.workflows_wanted)
    if runbooks:
        print(f"   - runbooks: {', '.join(runbooks)}")
    else:
        print("   - runbooks: choose based on selected workflows")
    print("6. Continue implementation only in the target repository")

    print()
    if prompt_yes_no(
        "I can copy everything needed from this guide and from official AWB to a new project directory. Do it now",
        default_yes=False,
    ):
        default_target = f"~/Documents/GitHub/{data.project_slug}"
        target_dir_text = prompt("Target project directory", default_target)
        guide_dir = Path(__file__).resolve().parent.parent
        copied, skipped, warnings = copy_bootstrap_assets(
            guide_dir=guide_dir,
            data=data,
            json_path=json_path,
            md_path=md_path,
            creation_template_path=creation_template_path,
            target_dir_text=target_dir_text,
        )

        print()
        print("Copy report:")
        print(f"- Copied: {len(copied)}")
        for path in copied:
            if path == "BUNDLE_VERIFICATION:PASS":
                continue
            print(f"  - {path}")
        print(f"- Skipped (already existed): {len(skipped)}")
        for path in skipped:
            print(f"  - {path}")
        print(f"- Warnings: {len(warnings)}")
        for item in warnings:
            print(f"  - {item}")

        bundle_ok = "BUNDLE_VERIFICATION:PASS" in copied and not warnings
        if bundle_ok:
            print("- Bundle verification: PASS (all required artifacts are present)")
        else:
            print("- Bundle verification: FAIL (review warnings/missing artifacts)")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
