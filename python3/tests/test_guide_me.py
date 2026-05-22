from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import runpy
import subprocess

import pytest

import guide_me
from helpers import BlueprintInputs


def _data(notes: list[str] | None = None, workflows: list[str] | None = None) -> BlueprintInputs:
    return BlueprintInputs(
        project_slug="proj-x",
        base_branch="main",
        existing_root_doc="AGENTS.md",
        workflows_wanted=workflows or ["document"],
        tech_stack=["Python"],
        core_rules=["core"],
        stack_specific_rules=["stack"],
        notes=notes if notes is not None else ["note"],
        collected_at_utc="2026-05-22T00:00:00+00:00",
    )


def test_print_input_guidance(capsys: pytest.CaptureFixture[str]) -> None:
    guide_me.print_input_guidance()
    out = capsys.readouterr().out
    assert "Input guidance" in out
    assert "Official AWB" in out


def test_markdown_and_creation_template_variants() -> None:
    with_notes = _data(notes=["n1"], workflows=["document", "linear"])
    without_notes = _data(notes=[], workflows=[])

    md_with = guide_me.to_markdown(with_notes)
    assert "## Notes" in md_with
    assert "- n1" in md_with
    assert "Copy related runbooks" in md_with

    md_without = guide_me.to_markdown(without_notes)
    assert "- (none)" in md_without

    creation = guide_me.to_creation_template(with_notes)
    assert "# Blueprint Used on Creation" in creation
    assert "Copy runbook from official AWB" in creation


def test_write_outputs_creates_expected_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_file = tmp_path / "python3" / "guide_me.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# placeholder", encoding="utf-8")
    monkeypatch.setattr(guide_me, "__file__", str(fake_file))

    fixed_now = datetime(2026, 5, 22, 1, 2, 3, tzinfo=timezone.utc)

    class FakeDatetime:
        @staticmethod
        def now(_tz):
            return fixed_now

    monkeypatch.setattr(guide_me, "datetime", FakeDatetime)

    data = _data()
    json_path, md_path, creation_path = guide_me.write_outputs(data)

    assert json_path.exists()
    assert md_path.exists()
    assert creation_path.exists()
    assert "blueprint_inputs_proj-x_20260522T010203Z" in json_path.name


def test_run_pre_bootstrap_audit_file_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_file = Path("/tmp/guide_me.py")
    monkeypatch.setattr(guide_me, "__file__", str(fake_file))

    def raise_file_not_found(*_args, **_kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)
    assert guide_me.run_pre_bootstrap_audit() is False


def test_run_pre_bootstrap_audit_failure_and_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_file = Path("/tmp/guide_me.py")
    monkeypatch.setattr(guide_me, "__file__", str(fake_file))

    class Result:
        def __init__(self, code: int, stdout: str, stderr: str) -> None:
            self.returncode = code
            self.stdout = stdout
            self.stderr = stderr

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: Result(1, "[WARN] something", "[FAIL] issue"),
    )
    assert guide_me.run_pre_bootstrap_audit() is False
    out = capsys.readouterr().out
    assert "Pre-bootstrap audit failed." in out

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_a, **_k: Result(0, "all good", ""),
    )
    assert guide_me.run_pre_bootstrap_audit() is True


def test_run_returns_one_when_audit_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guide_me, "run_pre_bootstrap_audit", lambda: False)
    assert guide_me.run() == 1


def test_run_happy_path_without_copy(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(guide_me, "run_pre_bootstrap_audit", lambda: True)
    monkeypatch.setattr(guide_me, "print_input_guidance", lambda: None)

    prompt_values = iter(["Bad Slug", "good-slug", "main", "AGENTS.md"])
    monkeypatch.setattr(guide_me, "prompt", lambda *_a, **_k: next(prompt_values))

    monkeypatch.setattr(
        guide_me,
        "prompt_csv_list",
        lambda *_a, **_k: ["document", "unknown", "document"],
    )

    multiline_values = iter([
        ["Python", "FastAPI"],
        ["core-a", "core-b"],
        ["stack-a"],
        ["n1"],
    ])
    monkeypatch.setattr(guide_me, "prompt_multiline", lambda *_a, **_k: next(multiline_values))

    yes_no_values = iter([False, False, False])
    monkeypatch.setattr(guide_me, "prompt_yes_no", lambda *_a, **_k: next(yes_no_values))

    out_json = tmp_path / "in.json"
    out_md = tmp_path / "in.md"
    out_creation = tmp_path / "blue_print_used_on_creation.md"
    out_json.write_text("{}", encoding="utf-8")
    out_md.write_text("# md", encoding="utf-8")
    out_creation.write_text("# creation", encoding="utf-8")
    monkeypatch.setattr(guide_me, "write_outputs", lambda _data: (out_json, out_md, out_creation))

    code = guide_me.run()
    assert code == 0


def test_run_copy_bundle_pass_and_fail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(guide_me, "run_pre_bootstrap_audit", lambda: True)
    monkeypatch.setattr(guide_me, "print_input_guidance", lambda: None)

    prompt_values = iter(["proj-y", "main", "AGENTS.md", str(tmp_path / "target")])
    monkeypatch.setattr(guide_me, "prompt", lambda *_a, **_k: next(prompt_values))

    monkeypatch.setattr(guide_me, "prompt_csv_list", lambda *_a, **_k: ["unknown"])
    multiline_values = iter([["Python"], ["notes"]])
    monkeypatch.setattr(guide_me, "prompt_multiline", lambda *_a, **_k: next(multiline_values))

    yes_no_values = iter([True, True, True])
    monkeypatch.setattr(guide_me, "prompt_yes_no", lambda *_a, **_k: next(yes_no_values))

    out_json = tmp_path / "in2.json"
    out_md = tmp_path / "in2.md"
    out_creation = tmp_path / "blue_print_used_on_creation.md"
    out_json.write_text("{}", encoding="utf-8")
    out_md.write_text("# md", encoding="utf-8")
    out_creation.write_text("# creation", encoding="utf-8")
    monkeypatch.setattr(guide_me, "write_outputs", lambda _data: (out_json, out_md, out_creation))

    monkeypatch.setattr(
        guide_me,
        "copy_bootstrap_assets",
        lambda **_k: (["copied-a", "BUNDLE_VERIFICATION:PASS"], ["skip-a"], []),
    )
    assert guide_me.run() == 0

    # Second run: same prompts, but force bundle verification fail reporting.
    prompt_values_2 = iter(["proj-z", "main", "AGENTS.md", str(tmp_path / "target2")])
    monkeypatch.setattr(guide_me, "prompt", lambda *_a, **_k: next(prompt_values_2))
    monkeypatch.setattr(guide_me, "prompt_csv_list", lambda *_a, **_k: ["unknown"])
    multiline_values_2 = iter([["Python"], ["notes"]])
    monkeypatch.setattr(guide_me, "prompt_multiline", lambda *_a, **_k: next(multiline_values_2))
    yes_no_values_2 = iter([True, True, True])
    monkeypatch.setattr(guide_me, "prompt_yes_no", lambda *_a, **_k: next(yes_no_values_2))

    monkeypatch.setattr(
        guide_me,
        "copy_bootstrap_assets",
        lambda **_k: (["copied-b"], ["skip-b"], ["warn-a"]),
    )
    assert guide_me.run() == 0


def test_main_guard_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    class Result:
        returncode = 1
        stdout = ""
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: Result())
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("guide_me", run_name="__main__")
    assert exc.value.code == 1
