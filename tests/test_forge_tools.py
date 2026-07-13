"""Pytest suite for the FORGE skill's Python CLI tools.

Exercises each tool in .claude/skills/forge/tools/ end-to-end via subprocess,
always running with cwd=tmp_path so the repo's own .forge/ directory (if one
exists) is never touched or mutated.

Assertions favor exit codes and file contents over stdout prose, since the
human-readable messages the tools print are cosmetic and may change. The
exceptions are a handful of checks against `forge_status.py --validate`
output, where the printed checklist text is copied verbatim from the cycle
template (not paraphrased prose) and is the only observable signal for that
code path, since validation has no file side effects.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TOOLS_DIR = Path(__file__).resolve().parents[1] / ".claude/skills/forge/tools"

FORGE_INIT = TOOLS_DIR / "forge_init.py"
FORGE_CYCLE = TOOLS_DIR / "forge_cycle.py"
FORGE_STATUS = TOOLS_DIR / "forge_status.py"
FORGE_PHASE = TOOLS_DIR / "forge_phase.py"
FORGE_LEARN = TOOLS_DIR / "forge_learn.py"


def run(tool: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run one of the FORGE CLI tools as a subprocess rooted at `cwd`."""
    return subprocess.run(
        [sys.executable, str(tool), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def active_cycle_files(project: Path) -> list[Path]:
    return sorted((project / ".forge" / "cycles" / "active").glob("*.md"))


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A tmp_path directory with FORGE initialized in it."""
    result = run(FORGE_INIT, ["--name", "demo-project"], tmp_path)
    assert result.returncode == 0
    return tmp_path


@pytest.fixture
def cycle(project: Path) -> Path:
    """`project` plus one fresh active full-mode cycle. Returns the cycle file."""
    result = run(FORGE_CYCLE, ["new", "Widget Feature"], project)
    assert result.returncode == 0
    files = active_cycle_files(project)
    assert len(files) == 1
    return files[0]


# ---------------------------------------------------------------------------
# forge_init.py
# ---------------------------------------------------------------------------


class TestForgeInit:
    def test_creates_forge_structure(self, tmp_path: Path):
        result = run(FORGE_INIT, ["--name", "demo-project"], tmp_path)
        assert result.returncode == 0

        forge_dir = tmp_path / ".forge"
        assert (forge_dir / "config.yaml").is_file()
        assert (forge_dir / "context.md").is_file()
        assert (forge_dir / "learnings.md").is_file()
        assert (forge_dir / "cycles" / "active").is_dir()
        assert (forge_dir / "cycles" / "completed").is_dir()

        config = yaml.safe_load((forge_dir / "config.yaml").read_text())
        assert config["project"] == "demo-project"
        assert config["phases"] == [
            "Focus",
            "Orchestrate",
            "Refine",
            "Generate",
            "Evaluate",
        ]

        assert "demo-project" in (forge_dir / "context.md").read_text()
        assert "# FORGE Learnings" in (forge_dir / "learnings.md").read_text()

    def test_default_name_is_directory_name(self, tmp_path: Path):
        result = run(FORGE_INIT, [], tmp_path)
        assert result.returncode == 0
        config = yaml.safe_load((tmp_path / ".forge" / "config.yaml").read_text())
        assert config["project"] == tmp_path.name

    def test_explicit_empty_name_falls_back_to_directory_name(self, tmp_path: Path):
        # Current behavior: `--name ""` is falsy in Python, so initialize()
        # silently falls back to the directory name instead of rejecting the
        # empty value. Documented here rather than treated as a bug.
        result = run(FORGE_INIT, ["--name", ""], tmp_path)
        assert result.returncode == 0
        config = yaml.safe_load((tmp_path / ".forge" / "config.yaml").read_text())
        assert config["project"] == tmp_path.name

    def test_second_init_fails_and_does_not_clobber_existing_state(self, tmp_path: Path):
        first = run(FORGE_INIT, ["--name", "demo-project"], tmp_path)
        assert first.returncode == 0
        config_before = (tmp_path / ".forge" / "config.yaml").read_text()

        second = run(FORGE_INIT, ["--name", "different-name"], tmp_path)
        assert second.returncode == 1

        config_after = (tmp_path / ".forge" / "config.yaml").read_text()
        assert config_after == config_before


# ---------------------------------------------------------------------------
# forge_cycle.py
# ---------------------------------------------------------------------------


class TestForgeCycle:
    def test_new_creates_cycle_with_focus_active_marker(self, project: Path):
        result = run(FORGE_CYCLE, ["new", "Widget Feature"], project)
        assert result.returncode == 0

        files = active_cycle_files(project)
        assert len(files) == 1
        content = files[0].read_text()
        assert "<!-- FORGE_PHASE:Focus:Active -->" in content
        assert files[0].name.endswith("-widget-feature.md")

    def test_new_without_forge_initialized_fails(self, tmp_path: Path):
        result = run(FORGE_CYCLE, ["new", "Widget Feature"], tmp_path)
        assert result.returncode == 1
        assert not (tmp_path / ".forge").exists()

    def test_new_missing_name_argument_is_argparse_error(self, project: Path):
        result = run(FORGE_CYCLE, ["new"], project)
        assert result.returncode == 2
        assert active_cycle_files(project) == []

    def test_new_empty_name_creates_degenerate_slug_file(self, project: Path):
        # Current behavior: slugify("") == "", so the cycle is still created,
        # just with a filename that is only the date prefix (e.g.
        # "20260713-.md") rather than being rejected as an invalid name.
        result = run(FORGE_CYCLE, ["new", ""], project)
        assert result.returncode == 0
        files = active_cycle_files(project)
        assert len(files) == 1
        assert files[0].stem.endswith("-")

    def test_new_name_with_only_punctuation_creates_degenerate_slug_file(self, project: Path):
        # Same underlying quirk as the empty-name case: a name with no
        # alphanumeric characters also slugifies to "".
        result = run(FORGE_CYCLE, ["new", "!!!"], project)
        assert result.returncode == 0
        files = active_cycle_files(project)
        assert len(files) == 1
        assert files[0].stem.endswith("-")

    def test_new_duplicate_name_same_day_fails(self, project: Path):
        first = run(FORGE_CYCLE, ["new", "Widget Feature"], project)
        assert first.returncode == 0
        second = run(FORGE_CYCLE, ["new", "Widget Feature"], project)
        assert second.returncode == 1
        assert len(active_cycle_files(project)) == 1

    def test_list_runs_and_exits_zero(self, cycle: Path, project: Path):
        result = run(FORGE_CYCLE, ["list"], project)
        assert result.returncode == 0

    def test_complete_before_evaluate_phase_fails(self, cycle: Path, project: Path):
        result = run(FORGE_CYCLE, ["complete", cycle.stem], project)
        assert result.returncode == 1
        assert cycle.exists()
        assert not (project / ".forge" / "cycles" / "completed" / cycle.name).exists()

    def test_complete_unknown_cycle_id_fails(self, cycle: Path, project: Path):
        result = run(FORGE_CYCLE, ["complete", "does-not-exist"], project)
        assert result.returncode == 1

    def test_complete_moves_file_once_cycle_reaches_evaluate(self, cycle: Path, project: Path):
        for _ in range(4):  # Focus -> Orchestrate -> Refine -> Generate -> Evaluate
            advanced = run(FORGE_PHASE, ["advance", "--force"], project)
            assert advanced.returncode == 0
        assert "<!-- FORGE_PHASE:Evaluate:Active -->" in cycle.read_text()

        result = run(FORGE_CYCLE, ["complete", cycle.stem], project)
        assert result.returncode == 0
        assert not cycle.exists()
        completed = project / ".forge" / "cycles" / "completed" / cycle.name
        assert completed.exists()


# ---------------------------------------------------------------------------
# forge_status.py
# ---------------------------------------------------------------------------


class TestForgeStatus:
    def test_status_without_forge_does_not_traceback_and_exits_zero(self, tmp_path: Path):
        # Current behavior: a missing .forge/ is reported as a message, not
        # treated as a hard error - the tool always returns 0.
        result = run(FORGE_STATUS, [], tmp_path)
        assert result.returncode == 0
        assert result.stderr == ""

    def test_validate_without_forge_does_not_traceback_and_exits_zero(self, tmp_path: Path):
        result = run(FORGE_STATUS, ["--validate"], tmp_path)
        assert result.returncode == 0
        assert result.stderr == ""

    def test_status_with_no_active_cycles_exits_zero(self, project: Path):
        result = run(FORGE_STATUS, [], project)
        assert result.returncode == 0

    def test_status_with_active_cycle_exits_zero(self, cycle: Path, project: Path):
        result = run(FORGE_STATUS, [], project)
        assert result.returncode == 0

    def test_status_detailed_flag_exits_zero(self, cycle: Path, project: Path):
        result = run(FORGE_STATUS, ["--detailed"], project)
        assert result.returncode == 0

    def test_validate_reports_incomplete_items_for_fresh_cycle(self, cycle: Path, project: Path):
        result = run(FORGE_STATUS, ["--validate"], project)
        assert result.returncode == 0
        # These lines come verbatim from the Focus phase checklist in
        # forge_cycle.py's CYCLE_TEMPLATE, not from decorative formatting.
        assert "Problem statement and target users defined" in result.stdout
        assert "Testable success criteria written" in result.stdout

    def test_validate_reports_ready_once_active_phase_items_are_checked(
        self, cycle: Path, project: Path
    ):
        # Manually check every box in the template (all phases) so the
        # active Focus phase - the only one validate cares about - reads
        # as fully complete.
        cycle.write_text(cycle.read_text().replace("- [ ]", "- [x]"))

        result = run(FORGE_STATUS, ["--validate"], project)
        assert result.returncode == 0
        assert "Problem statement and target users defined" not in result.stdout


# ---------------------------------------------------------------------------
# forge_phase.py
# ---------------------------------------------------------------------------


class TestForgePhase:
    def test_advance_without_forge_fails(self, tmp_path: Path):
        result = run(FORGE_PHASE, ["advance"], tmp_path)
        assert result.returncode == 1

    def test_advance_force_without_forge_fails(self, tmp_path: Path):
        result = run(FORGE_PHASE, ["advance", "--force"], tmp_path)
        assert result.returncode == 1

    def test_complete_task_without_forge_fails(self, tmp_path: Path):
        result = run(FORGE_PHASE, ["complete-task", "anything"], tmp_path)
        assert result.returncode == 1

    def test_add_task_without_forge_fails(self, tmp_path: Path):
        result = run(FORGE_PHASE, ["add-task", "anything"], tmp_path)
        assert result.returncode == 1

    def test_advance_without_force_is_refused_when_items_incomplete(
        self, cycle: Path, project: Path
    ):
        before = cycle.read_text()
        result = run(FORGE_PHASE, ["advance"], project)
        assert result.returncode == 1
        assert cycle.read_text() == before
        assert "<!-- FORGE_PHASE:Focus:Active -->" in cycle.read_text()

    def test_advance_with_force_succeeds_and_moves_to_orchestrate(
        self, cycle: Path, project: Path
    ):
        result = run(FORGE_PHASE, ["advance", "--force"], project)
        assert result.returncode == 0
        content = cycle.read_text()
        assert "<!-- FORGE_PHASE:Focus:Complete -->" in content
        assert "<!-- FORGE_PHASE:Orchestrate:Active -->" in content

    def test_advance_at_final_phase_fails(self, cycle: Path, project: Path):
        for _ in range(4):  # walk to Evaluate
            result = run(FORGE_PHASE, ["advance", "--force"], project)
            assert result.returncode == 0
        assert "<!-- FORGE_PHASE:Evaluate:Active -->" in cycle.read_text()

        result = run(FORGE_PHASE, ["advance", "--force"], project)
        assert result.returncode == 1

    def test_complete_task_marks_matching_checkbox(self, cycle: Path, project: Path):
        advanced = run(FORGE_PHASE, ["advance", "--force"], project)  # now in Orchestrate
        assert advanced.returncode == 0

        result = run(FORGE_PHASE, ["complete-task", "Container architecture"], project)
        assert result.returncode == 0
        assert "- [x] Container architecture (C4 L2) designed" in cycle.read_text()

    def test_complete_task_no_match_fails_and_leaves_file_untouched(
        self, cycle: Path, project: Path
    ):
        before = cycle.read_text()
        result = run(FORGE_PHASE, ["complete-task", "totally unrelated nonsense"], project)
        assert result.returncode == 1
        assert cycle.read_text() == before

    def test_add_task_appends_unchecked_item_to_active_phase(self, cycle: Path, project: Path):
        result = run(FORGE_PHASE, ["add-task", "Write onboarding doc"], project)
        assert result.returncode == 0
        assert "- [ ] Write onboarding doc" in cycle.read_text()


# ---------------------------------------------------------------------------
# forge_learn.py
# ---------------------------------------------------------------------------


class TestForgeLearn:
    def test_add_without_forge_fails(self, tmp_path: Path):
        result = run(FORGE_LEARN, ["add", "pattern", "Title", "Desc"], tmp_path)
        assert result.returncode == 1

    def test_list_without_learnings_file_exits_zero_despite_reporting_error(
        self, tmp_path: Path
    ):
        # Quirk in forge_learn.py: list_learnings() prints an error when
        # learnings.md is missing, but main() always returns 0 for the
        # `list` subcommand regardless of that outcome.
        result = run(FORGE_LEARN, ["list"], tmp_path)
        assert result.returncode == 0

    def test_add_invalid_category_is_argparse_error(self, project: Path):
        result = run(FORGE_LEARN, ["add", "bogus-category", "Title", "Desc"], project)
        assert result.returncode == 2

    def test_add_appends_entry_under_matching_section(self, project: Path):
        learnings_path = project / ".forge" / "learnings.md"
        before = learnings_path.read_text()

        result = run(
            FORGE_LEARN,
            [
                "add",
                "pattern",
                "Use fixtures",
                "Fixtures reduce duplication",
                "--context",
                "test suite",
            ],
            project,
        )
        assert result.returncode == 0

        after = learnings_path.read_text()
        assert after != before
        assert "### Use fixtures" in after
        assert "Fixtures reduce duplication" in after
        assert "**Context**: test suite" in after
        # Appended under Patterns, ahead of the next section header.
        assert after.index("## Patterns") < after.index("### Use fixtures") < after.index(
            "## Anti-Patterns"
        )

    def test_add_anti_pattern_category(self, project: Path):
        result = run(FORGE_LEARN, ["add", "anti-pattern", "Avoid X", "Because Y"], project)
        assert result.returncode == 0
        learnings = (project / ".forge" / "learnings.md").read_text()
        assert "### Avoid X" in learnings

    def test_list_after_adding_learning_exits_zero(self, project: Path):
        added = run(FORGE_LEARN, ["add", "tool", "ripgrep", "Fast search"], project)
        assert added.returncode == 0
        result = run(FORGE_LEARN, ["list"], project)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# End-to-end happy path
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_full_lifecycle_happy_path(self, tmp_path: Path):
        # 1. init creates .forge structure
        init_result = run(FORGE_INIT, ["--name", "e2e-project"], tmp_path)
        assert init_result.returncode == 0
        forge_dir = tmp_path / ".forge"
        assert (forge_dir / "config.yaml").is_file()
        assert (forge_dir / "context.md").is_file()
        assert (forge_dir / "learnings.md").is_file()
        assert (forge_dir / "cycles" / "active").is_dir()

        # 2. new cycle creates a file with the Focus:Active marker
        new_result = run(FORGE_CYCLE, ["new", "End To End Feature"], tmp_path)
        assert new_result.returncode == 0
        files = active_cycle_files(tmp_path)
        assert len(files) == 1
        cycle_file = files[0]
        assert "<!-- FORGE_PHASE:Focus:Active -->" in cycle_file.read_text()

        # 3. status runs exit 0
        status_result = run(FORGE_STATUS, [], tmp_path)
        assert status_result.returncode == 0

        # 4. validate reports incomplete
        validate_result = run(FORGE_STATUS, ["--validate"], tmp_path)
        assert validate_result.returncode == 0
        assert "Problem statement and target users defined" in validate_result.stdout

        # 5. advance without --force is refused
        refused = run(FORGE_PHASE, ["advance"], tmp_path)
        assert refused.returncode == 1
        assert "<!-- FORGE_PHASE:Focus:Active -->" in cycle_file.read_text()

        # 6. advance --force succeeds and moves to Orchestrate
        forced = run(FORGE_PHASE, ["advance", "--force"], tmp_path)
        assert forced.returncode == 0
        content = cycle_file.read_text()
        assert "<!-- FORGE_PHASE:Focus:Complete -->" in content
        assert "<!-- FORGE_PHASE:Orchestrate:Active -->" in content

        # 7. complete-task marks a task
        task_result = run(FORGE_PHASE, ["complete-task", "Container architecture"], tmp_path)
        assert task_result.returncode == 0
        assert "- [x] Container architecture (C4 L2) designed" in cycle_file.read_text()

        # 8. learn add appends to learnings.md
        learnings_path = forge_dir / "learnings.md"
        before_learnings = learnings_path.read_text()
        learn_result = run(
            FORGE_LEARN,
            ["add", "decision", "Adopt FORGE", "Chose FORGE for IDD workflow"],
            tmp_path,
        )
        assert learn_result.returncode == 0
        after_learnings = learnings_path.read_text()
        assert after_learnings != before_learnings
        assert "### Adopt FORGE" in after_learnings
        assert "Chose FORGE for IDD workflow" in after_learnings
