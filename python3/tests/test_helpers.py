from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

import helpers
from helpers import BlueprintInputs


def _sample_inputs(workflows: list[str] | None = None, project_mode: str = "new") -> BlueprintInputs:
    return BlueprintInputs(
        project_slug="sample-project",
        base_branch="main",
        existing_root_doc="AGENTS.md",
        workflows_wanted=workflows or ["document", "linear", "mcp-linear-sync"],
        tech_stack=["Python"],
        core_rules=["core"],
        stack_specific_rules=["stack"],
        notes=["note"],
        collected_at_utc="2026-05-22T00:00:00+00:00",
        project_mode=project_mode,
    )


def test_prompt_uses_input_and_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: " value ")
    assert helpers.prompt("Question", "fallback") == "value"

    monkeypatch.setattr("builtins.input", lambda _: "")
    assert helpers.prompt("Question", "fallback") == "fallback"
    assert helpers.prompt("Question") == ""


def test_prompt_yes_no_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert helpers.prompt_yes_no("Q", default_yes=True) is True

    monkeypatch.setattr("builtins.input", lambda _: "")
    assert helpers.prompt_yes_no("Q", default_yes=False) is False

    monkeypatch.setattr("builtins.input", lambda _: "YeS")
    assert helpers.prompt_yes_no("Q", default_yes=False) is True

    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert helpers.prompt_yes_no("Q", default_yes=True) is False


def test_prompt_project_mode_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert helpers.prompt_project_mode() == helpers.PROJECT_MODE_NEW

    monkeypatch.setattr("builtins.input", lambda _: "2")
    assert helpers.prompt_project_mode() == helpers.PROJECT_MODE_EXISTING

    monkeypatch.setattr("builtins.input", lambda _: "existing")
    assert helpers.prompt_project_mode() == helpers.PROJECT_MODE_EXISTING

    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert helpers.prompt_project_mode() == helpers.PROJECT_MODE_NEW

    monkeypatch.setattr("builtins.input", lambda _: "bogus")
    assert helpers.prompt_project_mode(default_mode=helpers.PROJECT_MODE_EXISTING) == (
        helpers.PROJECT_MODE_EXISTING
    )


def test_prompt_csv_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(helpers, "prompt", lambda _text, _default: " A, b , ,C ")
    assert helpers.prompt_csv_list("Q", ["x"]) == ["a", "b", "c"]

    monkeypatch.setattr(helpers, "prompt", lambda _text, _default: "")
    assert helpers.prompt_csv_list("Q", ["x", "y"]) == ["x", "y"]


def test_prompt_multiline_with_defaults_and_manual_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_then_blank = iter(["", "ignored"])
    monkeypatch.setattr("builtins.input", lambda _: next(first_then_blank))
    assert helpers.prompt_multiline("Q", defaults=["d1", "d2"]) == ["d1", "d2"]

    lines = iter(["one", "two", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(lines))
    assert helpers.prompt_multiline("Q") == ["one", "two"]


def test_simple_collection_helpers() -> None:
    assert helpers.unique_in_order(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]
    assert helpers.validate_slug("a-1") == "a-1"
    with pytest.raises(ValueError):
        helpers.validate_slug("BadSlug")


def test_recommended_runbooks_paths_and_resolution(tmp_path: Path) -> None:
    runbooks = helpers.recommended_runbooks(
        ["document", "linear", "mcp-linear-sync", "plan-to-blueprint"]
    )
    assert runbooks == [
        "document-review-changelog.md",
        "linear-mcp.md",
        "mcp-linear-sync.md",
        "plan-to-blueprint.md",
    ]

    guide_dir = tmp_path / "guide"
    guide_dir.mkdir()
    resolved = helpers.resolve_official_awb_dir(guide_dir)
    assert resolved == (guide_dir / "../agentic-workflow-blueprint").resolve()


def test_validate_target_dir_rejects_guide_subdir(tmp_path: Path) -> None:
    guide_dir = tmp_path / "guide"
    guide_dir.mkdir(parents=True)
    invalid_target = guide_dir / "loto"

    with pytest.raises(ValueError):
        helpers.validate_target_dir(guide_dir=guide_dir, target_dir=invalid_target)


def test_validate_target_dir_accepts_external_path(tmp_path: Path) -> None:
    guide_dir = tmp_path / "guide"
    target_dir = tmp_path / "new-project"
    guide_dir.mkdir(parents=True)

    helpers.validate_target_dir(guide_dir=guide_dir, target_dir=target_dir)


def test_validate_existing_target_dir(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"
    with pytest.raises(ValueError):
        helpers.validate_existing_target_dir(missing_dir)

    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    helpers.validate_existing_target_dir(existing_dir)


def test_has_existing_root_doc(tmp_path: Path) -> None:
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    assert helpers.has_existing_root_doc(target_dir, "CONTEXT.md") is False

    (target_dir / "CLAUDE.md").write_text("claude", encoding="utf-8")
    assert helpers.has_existing_root_doc(target_dir, "CONTEXT.md") is True

    other_dir = tmp_path / "other"
    other_dir.mkdir()
    (other_dir / "CONTEXT.md").write_text("context", encoding="utf-8")
    assert helpers.has_existing_root_doc(other_dir, "CONTEXT.md") is True


def test_discover_existing_context(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"
    assert helpers.discover_existing_context(missing_dir) == []

    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "README.md").write_text("readme", encoding="utf-8")
    (target_dir / "requirements.txt").write_text("reqs", encoding="utf-8")
    (target_dir / "main.py").write_text("print(1)", encoding="utf-8")
    (target_dir / ".git").mkdir()
    (target_dir / ".git" / "HEAD").write_text("ref", encoding="utf-8")
    docs_dir = target_dir / "DOCUMENTACAO_PROJETO"
    docs_dir.mkdir()
    (docs_dir / "notes.md").write_text("notes", encoding="utf-8")
    (docs_dir / "nested").mkdir()
    other_dir = target_dir / "assets"
    other_dir.mkdir()
    (other_dir / "logo.png").write_bytes(b"\x00")

    discovered = helpers.discover_existing_context(target_dir)
    assert "README.md" in discovered
    assert "requirements.txt" in discovered
    assert "main.py" not in discovered
    assert "DOCUMENTACAO_PROJETO/" in discovered
    assert "DOCUMENTACAO_PROJETO/notes.md" in discovered
    assert not any(item.startswith(".git") for item in discovered)
    assert not any(item.startswith("assets") for item in discovered)


def test_discover_existing_context_respects_depth_and_ignored_dirs(tmp_path: Path) -> None:
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Ignored library/build dirs must never be descended into.
    for ignored_name in ["node_modules", "vendor", "target", "site-packages", "some.egg-info"]:
        ignored_dir = target_dir / ignored_name
        ignored_dir.mkdir()
        (ignored_dir / "README.md").write_text("noise", encoding="utf-8")

    # Nested docs within depth (root -> level1 -> level2 -> level3 = depth 4).
    level1 = target_dir / "docs"
    level1.mkdir()
    level2 = level1 / "level2"
    level2.mkdir()
    level3 = level2 / "level3"
    level3.mkdir()
    (level3 / "deep.md").write_text("deep", encoding="utf-8")

    # One level beyond max depth must not be discovered.
    level4 = level3 / "level4"
    level4.mkdir()
    (level4 / "too_deep.md").write_text("too deep", encoding="utf-8")

    discovered = helpers.discover_existing_context(target_dir)
    assert "docs/level2/level3/deep.md" in discovered
    assert not any("too_deep.md" in item for item in discovered)
    for ignored_name in ["node_modules", "vendor", "target", "site-packages", "some.egg-info"]:
        assert not any(item.startswith(ignored_name) for item in discovered)


def test_render_project_context_md_empty_and_populated() -> None:
    empty_md = helpers.render_project_context_md([])
    assert "(none found)" in empty_md

    populated_md = helpers.render_project_context_md(["README.md", "docs/"])
    assert "- README.md" in populated_md
    assert "- docs/" in populated_md


def test_write_text_file_if_missing(tmp_path: Path) -> None:
    copied: list[str] = []
    skipped: list[str] = []
    warnings: list[str] = []

    dst = tmp_path / "nested" / "file.md"
    helpers.write_text_file_if_missing(dst, "content", copied, skipped, warnings)
    assert dst.read_text(encoding="utf-8") == "content"
    assert str(dst) in copied

    helpers.write_text_file_if_missing(dst, "other", copied, skipped, warnings)
    assert str(dst) in skipped
    assert dst.read_text(encoding="utf-8") == "content"


def test_copy_file_if_missing_and_copy_tree_if_missing(tmp_path: Path) -> None:
    copied: list[str] = []
    skipped: list[str] = []
    warnings: list[str] = []

    missing_src = tmp_path / "missing.txt"
    dst = tmp_path / "out" / "file.txt"
    helpers.copy_file_if_missing(missing_src, dst, copied, skipped, warnings)
    assert warnings and "Missing source file" in warnings[-1]

    warnings.clear()
    src = tmp_path / "src.txt"
    src.write_text("hello", encoding="utf-8")
    helpers.copy_file_if_missing(src, dst, copied, skipped, warnings)
    assert dst.read_text(encoding="utf-8") == "hello"

    helpers.copy_file_if_missing(src, dst, copied, skipped, warnings)
    assert str(dst) in skipped

    copied.clear()
    skipped.clear()
    warnings.clear()

    missing_dir = tmp_path / "missing-dir"
    out_dir = tmp_path / "out-tree"
    helpers.copy_tree_if_missing(missing_dir, out_dir, copied, skipped, warnings)
    assert warnings and "Missing source directory" in warnings[-1]

    warnings.clear()
    src_dir = tmp_path / "src-dir"
    (src_dir / "nested").mkdir(parents=True)
    (src_dir / "nested" / "file.txt").write_text("x", encoding="utf-8")
    helpers.copy_tree_if_missing(src_dir, out_dir, copied, skipped, warnings)
    assert (out_dir / "nested" / "file.txt").read_text(encoding="utf-8") == "x"

    helpers.copy_tree_if_missing(src_dir, out_dir, copied, skipped, warnings)
    assert str(out_dir) in skipped


def test_extract_findings_and_git_commit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    findings = helpers.extract_audit_findings("ok\n[WARN] A\n[FAIL] B\n")
    assert findings == ["[WARN] A", "[FAIL] B"]

    def raise_file_not_found(*_args, **_kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)
    assert helpers.get_git_commit(tmp_path) == "unknown"

    class Result:
        def __init__(self, code: int, stdout: str) -> None:
            self.returncode = code
            self.stdout = stdout

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: Result(1, ""))
    assert helpers.get_git_commit(tmp_path) == "unknown"

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: Result(0, "abc123\n"))
    assert helpers.get_git_commit(tmp_path) == "abc123"


def test_expected_verify_and_manifest(tmp_path: Path) -> None:
    data = _sample_inputs(["document", "linear"])
    target_dir = tmp_path / "target"
    target_dir.mkdir(parents=True)

    expected = helpers.expected_bundle_paths(target_dir, data, "in.json", "in.md")
    assert target_dir / "AGENTS.md" in expected
    assert target_dir / "runbooks" / "document-review-changelog.md" in expected
    assert target_dir / "bootstrap" / "PROJECT_CONTEXT.md" not in expected

    missing = helpers.verify_bootstrap_bundle(target_dir, data, "in.json", "in.md")
    assert missing

    official_awb_dir = tmp_path / "official"
    official_awb_dir.mkdir()

    manifest_path = helpers.write_bundle_manifest(
        target_dir=target_dir,
        official_awb_dir=official_awb_dir,
        data=data,
        input_json_name="in.json",
        input_md_name="in.md",
    )
    content = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert content["official_awb_repo"] == str(official_awb_dir)
    assert content["workflows_selected"] == ["document", "linear"]


def test_expected_bundle_paths_existing_mode_variants(tmp_path: Path) -> None:
    data = _sample_inputs(["document"], project_mode=helpers.PROJECT_MODE_EXISTING)

    no_root_doc_dir = tmp_path / "no-root-doc"
    no_root_doc_dir.mkdir()
    expected_without_root_doc = helpers.expected_bundle_paths(
        no_root_doc_dir, data, "in.json", "in.md"
    )
    assert no_root_doc_dir / "AGENTS.md" in expected_without_root_doc
    assert no_root_doc_dir / "bootstrap" / "PROJECT_CONTEXT.md" in expected_without_root_doc

    has_root_doc_dir = tmp_path / "has-root-doc"
    has_root_doc_dir.mkdir()
    (has_root_doc_dir / "AGENTS.md").write_text("agents", encoding="utf-8")
    expected_with_root_doc = helpers.expected_bundle_paths(
        has_root_doc_dir, data, "in.json", "in.md"
    )
    assert has_root_doc_dir / "AGENTS.md" not in expected_with_root_doc
    assert has_root_doc_dir / "bootstrap" / "PROJECT_CONTEXT.md" in expected_with_root_doc


def test_copy_bootstrap_assets_success_and_failure(tmp_path: Path) -> None:
    data = _sample_inputs(["document"])
    guide_dir = tmp_path / "guide"
    official = tmp_path / "agentic-workflow-blueprint"

    guide_dir.mkdir(parents=True)
    (guide_dir / "bootstrap_checklist.md").write_text("check", encoding="utf-8")
    (guide_dir / "agentic_workflow_blueprint_guidance.md").write_text("guide", encoding="utf-8")

    (official / "workflows" / "document").mkdir(parents=True)
    (official / "workflows" / "document" / "README.md").write_text("wf", encoding="utf-8")
    (official / "runbooks").mkdir(parents=True)
    (official / "runbooks" / "document-review-changelog.md").write_text("rb", encoding="utf-8")
    (official / "AGENTS.md").write_text("agents", encoding="utf-8")

    json_path = tmp_path / "inputs.json"
    md_path = tmp_path / "inputs.md"
    creation_path = tmp_path / "blue_print_used_on_creation.md"
    json_path.write_text("{}", encoding="utf-8")
    md_path.write_text("# md", encoding="utf-8")
    creation_path.write_text("# creation", encoding="utf-8")

    target_dir = tmp_path / "target"
    copied, skipped, warnings = helpers.copy_bootstrap_assets(
        guide_dir=guide_dir,
        data=data,
        json_path=json_path,
        md_path=md_path,
        creation_template_path=creation_path,
        target_dir_text=str(target_dir),
    )
    assert not skipped
    assert not warnings
    assert "BUNDLE_VERIFICATION:PASS" in copied

    # Remove source and target AGENTS so the second run cannot restore it,
    # which forces bundle verification failure.
    (official / "AGENTS.md").unlink()
    (target_dir / "AGENTS.md").unlink()
    copied2, skipped2, warnings2 = helpers.copy_bootstrap_assets(
        guide_dir=guide_dir,
        data=data,
        json_path=json_path,
        md_path=md_path,
        creation_template_path=creation_path,
        target_dir_text=str(target_dir),
    )
    assert skipped2
    assert copied2
    assert any("Bundle verification failed" in item for item in warnings2)


def test_copy_bootstrap_assets_existing_mode_requires_pre_existing_dir(tmp_path: Path) -> None:
    data = _sample_inputs(["document"], project_mode=helpers.PROJECT_MODE_EXISTING)
    guide_dir = tmp_path / "guide"
    official = tmp_path / "agentic-workflow-blueprint"

    guide_dir.mkdir(parents=True)
    (guide_dir / "bootstrap_checklist.md").write_text("check", encoding="utf-8")
    (guide_dir / "agentic_workflow_blueprint_guidance.md").write_text("guide", encoding="utf-8")

    (official / "workflows" / "document").mkdir(parents=True)
    (official / "workflows" / "document" / "README.md").write_text("wf", encoding="utf-8")
    (official / "runbooks").mkdir(parents=True)
    (official / "runbooks" / "document-review-changelog.md").write_text("rb", encoding="utf-8")
    (official / "AGENTS.md").write_text("agents", encoding="utf-8")

    json_path = tmp_path / "inputs.json"
    md_path = tmp_path / "inputs.md"
    creation_path = tmp_path / "blue_print_used_on_creation.md"
    json_path.write_text("{}", encoding="utf-8")
    md_path.write_text("# md", encoding="utf-8")
    creation_path.write_text("# creation", encoding="utf-8")

    missing_target = tmp_path / "existing-project-not-created"
    with pytest.raises(ValueError):
        helpers.copy_bootstrap_assets(
            guide_dir=guide_dir,
            data=data,
            json_path=json_path,
            md_path=md_path,
            creation_template_path=creation_path,
            target_dir_text=str(missing_target),
        )

    existing_target = tmp_path / "existing-project"
    existing_target.mkdir()
    copied, skipped, warnings = helpers.copy_bootstrap_assets(
        guide_dir=guide_dir,
        data=data,
        json_path=json_path,
        md_path=md_path,
        creation_template_path=creation_path,
        target_dir_text=str(existing_target),
    )
    assert not skipped
    assert not warnings
    assert "BUNDLE_VERIFICATION:PASS" in copied
    assert (existing_target / "bootstrap" / "PROJECT_CONTEXT.md").exists()
    assert (existing_target / "AGENTS.md").exists()

    context_md = (existing_target / "bootstrap" / "PROJECT_CONTEXT.md").read_text(
        encoding="utf-8"
    )
    assert "(none found)" in context_md
    assert "AGENTS.md" not in context_md
    assert "blue_print_used_on_creation.md" not in context_md


def test_copy_bootstrap_assets_existing_mode_skips_agents_md_when_root_doc_present(
    tmp_path: Path,
) -> None:
    data = _sample_inputs(["document"], project_mode=helpers.PROJECT_MODE_EXISTING)
    guide_dir = tmp_path / "guide"
    official = tmp_path / "agentic-workflow-blueprint"

    guide_dir.mkdir(parents=True)
    (guide_dir / "bootstrap_checklist.md").write_text("check", encoding="utf-8")
    (guide_dir / "agentic_workflow_blueprint_guidance.md").write_text("guide", encoding="utf-8")

    (official / "workflows" / "document").mkdir(parents=True)
    (official / "workflows" / "document" / "README.md").write_text("wf", encoding="utf-8")
    (official / "runbooks").mkdir(parents=True)
    (official / "runbooks" / "document-review-changelog.md").write_text("rb", encoding="utf-8")
    (official / "AGENTS.md").write_text("agents", encoding="utf-8")

    json_path = tmp_path / "inputs.json"
    md_path = tmp_path / "inputs.md"
    creation_path = tmp_path / "blue_print_used_on_creation.md"
    json_path.write_text("{}", encoding="utf-8")
    md_path.write_text("# md", encoding="utf-8")
    creation_path.write_text("# creation", encoding="utf-8")

    existing_target = tmp_path / "existing-project-with-root-doc"
    existing_target.mkdir()
    (existing_target / "CLAUDE.md").write_text("already here", encoding="utf-8")
    (existing_target / "README.md").write_text("project readme", encoding="utf-8")

    copied, skipped, warnings = helpers.copy_bootstrap_assets(
        guide_dir=guide_dir,
        data=data,
        json_path=json_path,
        md_path=md_path,
        creation_template_path=creation_path,
        target_dir_text=str(existing_target),
    )
    assert not (existing_target / "AGENTS.md").exists()
    assert any("AGENTS.md not copied" in item for item in skipped)
    assert not warnings
    assert "BUNDLE_VERIFICATION:PASS" in copied

    context_md = (existing_target / "bootstrap" / "PROJECT_CONTEXT.md").read_text(
        encoding="utf-8"
    )
    assert "CLAUDE.md" in context_md
    assert "README.md" in context_md
    assert "blue_print_used_on_creation.md" not in context_md
    assert "agentic_workflow_blueprint_guidance.md" not in context_md


def test_copy_bootstrap_assets_rejects_target_inside_guide(tmp_path: Path) -> None:
    data = _sample_inputs(["document"])
    guide_dir = tmp_path / "guide"
    official = tmp_path / "agentic-workflow-blueprint"

    guide_dir.mkdir(parents=True)
    (guide_dir / "bootstrap_checklist.md").write_text("check", encoding="utf-8")
    (guide_dir / "agentic_workflow_blueprint_guidance.md").write_text("guide", encoding="utf-8")

    (official / "workflows" / "document").mkdir(parents=True)
    (official / "workflows" / "document" / "README.md").write_text("wf", encoding="utf-8")
    (official / "runbooks").mkdir(parents=True)
    (official / "runbooks" / "document-review-changelog.md").write_text("rb", encoding="utf-8")
    (official / "AGENTS.md").write_text("agents", encoding="utf-8")

    json_path = tmp_path / "inputs.json"
    md_path = tmp_path / "inputs.md"
    creation_path = tmp_path / "blue_print_used_on_creation.md"
    json_path.write_text("{}", encoding="utf-8")
    md_path.write_text("# md", encoding="utf-8")
    creation_path.write_text("# creation", encoding="utf-8")

    with pytest.raises(ValueError):
        helpers.copy_bootstrap_assets(
            guide_dir=guide_dir,
            data=data,
            json_path=json_path,
            md_path=md_path,
            creation_template_path=creation_path,
            target_dir_text=str(guide_dir / "loto"),
        )
