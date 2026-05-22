from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

import helpers
from helpers import BlueprintInputs


def _sample_inputs(workflows: list[str] | None = None) -> BlueprintInputs:
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
    runbooks = helpers.recommended_runbooks(["document", "linear", "mcp-linear-sync"])
    assert runbooks == [
        "document-review-changelog.md",
        "linear-mcp.md",
        "mcp-linear-sync.md",
    ]

    guide_dir = tmp_path / "guide"
    guide_dir.mkdir()
    resolved = helpers.resolve_official_awb_dir(guide_dir)
    assert resolved == (guide_dir / "../agentic-workflow-blueprint").resolve()


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
