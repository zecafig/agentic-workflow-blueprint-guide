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
PROJECT_MODE_NEW = "new"
PROJECT_MODE_EXISTING = "existing"
PROJECT_MODES = {PROJECT_MODE_NEW, PROJECT_MODE_EXISTING}
DOC_CHAIN_WORKFLOWS = {"document", "review", "changelog"}
MCP_SYNC_WORKFLOWS = {"mcp-linear-planner", "mcp-linear-sync"}
KNOWN_WORKFLOWS = {
    "document",
    "review",
    "changelog",
    "linear",
    "mcp-linear-planner",
    "mcp-linear-sync",
    "plan-to-blueprint",
}

ROOT_DOC_CANDIDATES = ("AGENTS.md", "CLAUDE.md")
CONTEXT_SCAN_MAX_DEPTH = 4
CONTEXT_SCAN_IGNORED_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    "vendor",
    "site-packages",
    ".tox",
    "htmlcov",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".cache",
}
CONTEXT_SCAN_MANIFEST_NAMES = {
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "pom.xml",
    "build.gradle",
    "composer.json",
    "setup.py",
    "setup.cfg",
}
CONTEXT_SCAN_STRUCTURE_DIR_NAMES = {"docs", "documentation", "test", "tests", ".github"}

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
    project_mode: str = PROJECT_MODE_NEW


def prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{text}{suffix}: ").strip()
    if raw:
        return raw
    return default or ""


def prompt_project_mode(default_mode: str = PROJECT_MODE_NEW) -> str:
    print("Project mode:")
    print("  1) new - bootstrap a brand new project repository")
    print("  2) existing - apply this guide's docs/workflow files to an existing project")
    raw = prompt("Select project mode (new/existing)", default_mode).strip().lower()
    if raw in {"1", PROJECT_MODE_NEW}:
        return PROJECT_MODE_NEW
    if raw in {"2", PROJECT_MODE_EXISTING}:
        return PROJECT_MODE_EXISTING
    return default_mode


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
    if "plan-to-blueprint" in workflows:
        runbooks.append("plan-to-blueprint.md")

    return runbooks


def resolve_official_awb_dir(guide_dir: Path) -> Path:
    return (guide_dir / "../agentic-workflow-blueprint").resolve()


def validate_target_dir(guide_dir: Path, target_dir: Path) -> None:
    resolved_guide_dir = guide_dir.resolve()
    resolved_target_dir = target_dir.resolve()

    if resolved_target_dir == resolved_guide_dir or resolved_guide_dir in resolved_target_dir.parents:
        raise ValueError(
            "Target project directory cannot be inside this guide repository. "
            "Use a separate project directory typed by the user (for example: ~/Documents/GitHub/<project-slug>)."
        )


def validate_existing_target_dir(target_dir: Path) -> None:
    if not target_dir.is_dir():
        raise ValueError(
            "Existing project mode requires the target directory to already exist: "
            f"{target_dir}. Create or open the existing project repository first, "
            "then rerun this guide."
        )


def has_existing_root_doc(target_dir: Path, existing_root_doc: str) -> bool:
    candidates = {existing_root_doc, *ROOT_DOC_CANDIDATES}
    return any((target_dir / name).exists() for name in candidates)


def discover_existing_context(
    target_dir: Path, max_depth: int = CONTEXT_SCAN_MAX_DEPTH
) -> List[str]:
    if not target_dir.is_dir():
        return []

    found: List[str] = []
    _scan_context_tree(target_dir, target_dir, max_depth, found)
    return found


def _is_context_scan_dir_ignored(name: str) -> bool:
    if name in CONTEXT_SCAN_IGNORED_NAMES or name.endswith(".egg-info"):
        return True
    return name.startswith(".") and name != ".github"


def _scan_context_tree(root: Path, current: Path, depth_remaining: int, found: List[str]) -> None:
    if depth_remaining <= 0:
        return

    for entry in sorted(current.iterdir(), key=lambda p: p.name.lower()):
        name = entry.name
        if _is_context_scan_dir_ignored(name):
            continue

        relative = entry.relative_to(root).as_posix()

        if entry.is_file():
            if entry.suffix.lower() in {".md", ".rst"} or name in CONTEXT_SCAN_MANIFEST_NAMES:
                found.append(relative)
            continue

        if name in CONTEXT_SCAN_STRUCTURE_DIR_NAMES or "doc" in name.lower():
            found.append(f"{relative}/")

        _scan_context_tree(root, entry, depth_remaining - 1, found)


def render_project_context_md(discovered: List[str]) -> str:
    lines = [
        "# Project Context Index",
        "",
        "Files and directories already present in this project before AWB docs were added.",
        "Read these first before relying on generic AWB scaffolding for project specifics.",
        "",
    ]
    if discovered:
        lines.extend(f"- {item}" for item in discovered)
    else:
        lines.append("- (none found)")
    lines.append("")
    return "\n".join(lines)


def write_text_file_if_missing(
    dst: Path, content: str, copied: List[str], skipped: List[str], warnings: List[str]
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        skipped.append(str(dst))
        return

    dst.write_text(content, encoding="utf-8")
    copied.append(str(dst))


def append_project_context_link(agents_md_path: Path) -> None:
    note = (
        "\n## Project Context Index\n\n"
        "This is an existing project. Read `bootstrap/PROJECT_CONTEXT.md` for an index "
        "of context that already existed here before AWB docs were added.\n"
    )
    with agents_md_path.open("a", encoding="utf-8") as handle:
        handle.write(note)


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
    validate_target_dir(guide_dir=guide_dir, target_dir=target_dir)

    copied: List[str] = []
    skipped: List[str] = []
    warnings: List[str] = []

    if data.project_mode == PROJECT_MODE_EXISTING:
        validate_existing_target_dir(target_dir)
    else:
        target_dir.mkdir(parents=True, exist_ok=True)

    # Snapshot pre-existing context before any AWB files are written into target_dir.
    discovered_context = (
        discover_existing_context(target_dir) if data.project_mode == PROJECT_MODE_EXISTING else []
    )

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

    existing_root_doc_present = data.project_mode == PROJECT_MODE_EXISTING and has_existing_root_doc(
        target_dir, data.existing_root_doc
    )
    if existing_root_doc_present:
        skipped.append(
            "AGENTS.md not copied: existing root doc already present in target project "
            f"(matched one of: {data.existing_root_doc}, {', '.join(ROOT_DOC_CANDIDATES)})."
        )
    else:
        agents_md_path = target_dir / "AGENTS.md"
        copy_file_if_missing(
            official_awb_dir / "AGENTS.md",
            agents_md_path,
            copied,
            skipped,
            warnings,
        )
        if data.project_mode == PROJECT_MODE_EXISTING and str(agents_md_path) in copied:
            append_project_context_link(agents_md_path)

    if data.project_mode == PROJECT_MODE_EXISTING:
        write_text_file_if_missing(
            target_dir / "bootstrap" / "PROJECT_CONTEXT.md",
            render_project_context_md(discovered_context),
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
        target_dir / "blue_print_used_on_creation.md",
        target_dir / "bootstrap_checklist.md",
        target_dir / "agentic_workflow_blueprint_guidance.md",
        target_dir / "bootstrap" / "inputs" / input_json_name,
        target_dir / "bootstrap" / "inputs" / input_md_name,
    ]

    existing_root_doc_present = data.project_mode == PROJECT_MODE_EXISTING and has_existing_root_doc(
        target_dir, data.existing_root_doc
    )
    if not existing_root_doc_present:
        paths.append(target_dir / "AGENTS.md")

    if data.project_mode == PROJECT_MODE_EXISTING:
        paths.append(target_dir / "bootstrap" / "PROJECT_CONTEXT.md")

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
