from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import List

DEFAULT_WORKFLOWS = ["document", "review", "changelog"]
GENERATED_BLUEPRINTS_DIR = "generated_blueprints"
DOC_CHAIN_WORKFLOWS = {"document", "review", "changelog"}
MCP_SYNC_WORKFLOWS = {"mcp-linear-planner", "mcp-linear-sync"}
KNOWN_WORKFLOWS = {
    "document",
    "review",
    "changelog",
    "linear",
    "mcp-linear-planner",
    "mcp-linear-sync",
}

DEFAULT_CORE_RULES = [
    "Root doc remains minimal and links to canonical skill/workflow files",
    "Workflow IDs and file paths stay consistent across references",
    "Each workflow contract includes Goal, Scope, Triggers, Inputs, Invariants, Procedure, Outputs, Review gate, References",
    "Avoid duplication; link to the source of truth",
    "Scaffold only requested workflows",
    "All contract links resolve",
]

DEFAULT_STACK_SPECIFIC_RULES = [
    "Use TDD for any task.",
    "Run ruff check and ensure coverage is 100% before suggesting commit.",
    "Write Pythonic code.",
    "Avoid regressions.",
    "Always use .venv.",
    "In GitHub Actions workflows, set FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true to avoid deprecated Node runtimes.",
    "Keep CI running on push to main and on pull_request so every commit is validated.",
    "Keep README badges dynamic and linked to live CI/coverage sources; do not use static result badges.",
    "Always use Material Design for UI.",
    '"Clean the house" means checking for legacy or useless code.',
    "Always let the user test and review before suggesting a commit.",
]


@dataclass
class BlueprintInputs:
    project_slug: str
    base_branch: str
    existing_root_doc: str
    workflows_wanted: List[str]
    tech_stack: List[str]
    core_rules: List[str]
    stack_specific_rules: List[str]
    notes: List[str]
    collected_at_utc: str


def prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{text}{suffix}: ").strip()
    if raw:
        return raw
    return default or ""


def prompt_yes_no(text: str, default_yes: bool = True) -> bool:
    default = "Y/n" if default_yes else "y/N"
    answer = input(f"{text} [{default}]: ").strip().lower()
    if not answer:
        return default_yes
    return answer in {"y", "yes"}


def prompt_csv_list(text: str, default_values: List[str]) -> List[str]:
    default_csv = ", ".join(default_values)
    raw = prompt(text, default_csv)
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    return values or default_values


def prompt_multiline(text: str, defaults: List[str] | None = None) -> List[str]:
    print(text)
    print("Enter one item per line. Submit an empty line to finish.")
    if defaults:
        print("Press ENTER on the first line to keep defaults.")
    values: List[str] = []

    while True:
        line = input("- ").strip()
        if not line:
            if defaults and not values:
                return defaults
            break
        values.append(line)

    return values


def unique_in_order(values: List[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def validate_slug(value: str) -> str:
    if re.fullmatch(r"[a-z0-9][a-z0-9-]*", value):
        return value
    raise ValueError(
        "projectSlug must match [a-z0-9][a-z0-9-]* (lowercase letters, digits, hyphens)."
    )


def recommended_runbooks(workflows: List[str]) -> List[str]:
    runbooks: List[str] = []

    if any(w in workflows for w in DOC_CHAIN_WORKFLOWS):
        runbooks.append("document-review-changelog.md")
    if "linear" in workflows:
        runbooks.append("linear-mcp.md")
    if any(w in workflows for w in MCP_SYNC_WORKFLOWS):
        runbooks.append("mcp-linear-sync.md")

    return runbooks


def resolve_official_awb_dir(guide_dir: Path) -> Path:
    return (guide_dir / "../agentic-workflow-blueprint").resolve()


def copy_file_if_missing(
    src: Path, dst: Path, copied: List[str], skipped: List[str], warnings: List[str]
) -> None:
    if not src.exists():
        warnings.append(f"Missing source file: {src}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        skipped.append(str(dst))
        return

    shutil.copy2(src, dst)
    copied.append(str(dst))


def copy_tree_if_missing(
    src: Path, dst: Path, copied: List[str], skipped: List[str], warnings: List[str]
) -> None:
    if not src.exists():
        warnings.append(f"Missing source directory: {src}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        skipped.append(str(dst))
        return

    shutil.copytree(src, dst)
    copied.append(str(dst))


def copy_bootstrap_assets(
    guide_dir: Path,
    data: BlueprintInputs,
    json_path: Path,
    md_path: Path,
    creation_template_path: Path,
    target_dir_text: str,
) -> tuple[List[str], List[str], List[str]]:
    target_dir = Path(target_dir_text).expanduser().resolve()
    official_awb_dir = resolve_official_awb_dir(guide_dir)

    copied: List[str] = []
    skipped: List[str] = []
    warnings: List[str] = []

    target_dir.mkdir(parents=True, exist_ok=True)
    inputs_dir = target_dir / "bootstrap" / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    copy_file_if_missing(
        json_path, inputs_dir / json_path.name, copied, skipped, warnings
    )
    copy_file_if_missing(md_path, inputs_dir / md_path.name, copied, skipped, warnings)
    copy_file_if_missing(
        creation_template_path,
        target_dir / "blue_print_used_on_creation.md",
        copied,
        skipped,
        warnings,
    )

    copy_file_if_missing(
        guide_dir / "bootstrap_checklist.md",
        target_dir / "bootstrap_checklist.md",
        copied,
        skipped,
        warnings,
    )
    copy_file_if_missing(
        guide_dir / "agentic_workflow_blueprint_guidance.md",
        target_dir / "agentic_workflow_blueprint_guidance.md",
        copied,
        skipped,
        warnings,
    )

    copy_file_if_missing(
        official_awb_dir / "AGENTS.md",
        target_dir / "AGENTS.md",
        copied,
        skipped,
        warnings,
    )

    for workflow in data.workflows_wanted:
        copy_tree_if_missing(
            official_awb_dir / "workflows" / workflow,
            target_dir / "workflows" / workflow,
            copied,
            skipped,
            warnings,
        )

    for runbook in recommended_runbooks(data.workflows_wanted):
        copy_file_if_missing(
            official_awb_dir / "runbooks" / runbook,
            target_dir / "runbooks" / runbook,
            copied,
            skipped,
            warnings,
        )

    manifest_path = write_bundle_manifest(
        target_dir=target_dir,
        official_awb_dir=official_awb_dir,
        data=data,
        input_json_name=json_path.name,
        input_md_name=md_path.name,
    )
    copied.append(str(manifest_path))

    missing_paths = verify_bootstrap_bundle(
        target_dir=target_dir,
        data=data,
        input_json_name=json_path.name,
        input_md_name=md_path.name,
    )
    if missing_paths:
        warnings.append(
            f"Bundle verification failed: missing {len(missing_paths)} required artifact(s)."
        )
        warnings.extend(f"Missing target artifact: {path}" for path in missing_paths)
    else:
        copied.append("BUNDLE_VERIFICATION:PASS")

    return copied, skipped, warnings


def extract_audit_findings(output: str) -> List[str]:
    findings: List[str] = []
    for line in output.splitlines():
        if "[FAIL]" in line or "[WARN]" in line:
            findings.append(line.strip())
    return findings


def get_git_commit(repo_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "unknown"

    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def expected_bundle_paths(
    target_dir: Path,
    data: BlueprintInputs,
    input_json_name: str,
    input_md_name: str,
) -> List[Path]:
    paths = [
        target_dir / "AGENTS.md",
        target_dir / "blue_print_used_on_creation.md",
        target_dir / "bootstrap_checklist.md",
        target_dir / "agentic_workflow_blueprint_guidance.md",
        target_dir / "bootstrap" / "inputs" / input_json_name,
        target_dir / "bootstrap" / "inputs" / input_md_name,
    ]

    for workflow in data.workflows_wanted:
        paths.append(target_dir / "workflows" / workflow)
    for runbook in recommended_runbooks(data.workflows_wanted):
        paths.append(target_dir / "runbooks" / runbook)

    return paths


def verify_bootstrap_bundle(
    target_dir: Path,
    data: BlueprintInputs,
    input_json_name: str,
    input_md_name: str,
) -> List[str]:
    missing: List[str] = []
    for path in expected_bundle_paths(target_dir, data, input_json_name, input_md_name):
        if not path.exists():
            missing.append(str(path))
    return missing


def write_bundle_manifest(
    target_dir: Path,
    official_awb_dir: Path,
    data: BlueprintInputs,
    input_json_name: str,
    input_md_name: str,
) -> Path:
    manifest_dir = target_dir / "bootstrap"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "official_awb_manifest.json"

    manifest = {
        "official_awb_repo": str(official_awb_dir),
        "official_awb_commit": get_git_commit(official_awb_dir),
        "workflows_selected": data.workflows_wanted,
        "runbooks_selected": recommended_runbooks(data.workflows_wanted),
        "required_artifacts": [
            str(path)
            for path in expected_bundle_paths(
                target_dir=target_dir,
                data=data,
                input_json_name=input_json_name,
                input_md_name=input_md_name,
            )
        ],
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
