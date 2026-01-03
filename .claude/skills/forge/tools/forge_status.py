# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
FORGE Status Tool - Get cycle status and run checkpoints

Usage:
    uv run forge_status.py [cycle-id]
    uv run forge_status.py --validate
    uv run forge_status.py --all
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


PHASES = ["Focus", "Orchestrate", "Refine", "Generate", "Evaluate"]
PHASE_ICONS = {
    "Focus": "🎯",
    "Orchestrate": "📝",
    "Refine": "🔨",
    "Generate": "🚀",
    "Evaluate": "📊"
}


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    forge_dir = Path.cwd() / ".forge"
    if not forge_dir.exists():
        raise FileNotFoundError(".forge/ not found. Run forge_init.py first.")
    return forge_dir


def parse_cycle_file(path: Path) -> dict:
    """Parse a cycle markdown file into structured data."""
    content = path.read_text()

    # Extract feature name
    feature_match = re.search(r'^# Feature: (.+)$', content, re.MULTILINE)
    feature = feature_match.group(1) if feature_match else "Unknown"

    # Extract metadata
    created_match = re.search(r'\*\*Created\*\*: (.+)$', content, re.MULTILINE)
    status_match = re.search(r'\*\*Status\*\*: (.+)$', content, re.MULTILINE)
    priority_match = re.search(r'\*\*Priority\*\*: (.+)$', content, re.MULTILINE)

    # Parse phases
    phases = {}
    current_phase = None

    for i, phase in enumerate(PHASES):
        phase_pattern = rf'### Phase {i+1}: {phase} \[(\w+)\](.*?)(?=### Phase|\Z)'
        phase_match = re.search(phase_pattern, content, re.DOTALL)
        if phase_match:
            status = phase_match.group(1)
            tasks_content = phase_match.group(2)

            # Parse tasks
            tasks = []
            for m in re.finditer(r'- \[([x ])\] (.+)$', tasks_content, re.MULTILINE):
                tasks.append({
                    "completed": m.group(1) == "x",
                    "description": m.group(2).strip()
                })

            completed = len([t for t in tasks if t["completed"]])
            total = len(tasks)

            phases[phase.lower()] = {
                "status": status,
                "completed": completed,
                "total": total,
                "progress": round(completed / total * 100) if total > 0 else 0,
                "tasks": tasks
            }

            if status == "Active":
                current_phase = phase

    # Calculate overall progress
    total_tasks = sum(p["total"] for p in phases.values())
    completed_tasks = sum(p["completed"] for p in phases.values())
    overall_progress = round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return {
        "id": path.stem,
        "feature": feature,
        "created": created_match.group(1) if created_match else None,
        "status": status_match.group(1) if status_match else "Focus",
        "priority": priority_match.group(1) if priority_match else "medium",
        "current_phase": current_phase,
        "phases": phases,
        "overall_progress": overall_progress,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "path": str(path)
    }


def get_status(cycle_id: str = None, include_all: bool = False) -> dict:
    """Get status of cycles."""
    forge_dir = get_forge_dir()
    active_dir = forge_dir / "cycles" / "active"

    cycles = []

    if cycle_id:
        # Specific cycle
        cycle_path = active_dir / f"{cycle_id}.md"
        if not cycle_path.exists():
            # Check completed
            cycle_path = forge_dir / "cycles" / "completed" / f"{cycle_id}.md"
        if not cycle_path.exists():
            return {"success": False, "error": f"Cycle '{cycle_id}' not found"}
        cycles.append(parse_cycle_file(cycle_path))
    else:
        # All active cycles
        if active_dir.exists():
            for path in sorted(active_dir.glob("*.md")):
                cycles.append(parse_cycle_file(path))

        if include_all:
            completed_dir = forge_dir / "cycles" / "completed"
            if completed_dir.exists():
                for path in sorted(completed_dir.glob("*.md")):
                    cycle = parse_cycle_file(path)
                    cycle["completed"] = True
                    cycles.append(cycle)

    return {
        "success": True,
        "count": len(cycles),
        "cycles": cycles
    }


def validate_checkpoint(cycle_id: str = None) -> dict:
    """Run checkpoint validation on cycle."""
    forge_dir = get_forge_dir()
    active_dir = forge_dir / "cycles" / "active"

    # Find cycle
    if cycle_id:
        cycle_path = active_dir / f"{cycle_id}.md"
    else:
        cycles = list(active_dir.glob("*.md"))
        if len(cycles) == 0:
            return {"success": False, "error": "No active cycles"}
        if len(cycles) > 1:
            return {"success": False, "error": f"Multiple cycles. Specify one: {[c.stem for c in cycles]}"}
        cycle_path = cycles[0]

    if not cycle_path.exists():
        return {"success": False, "error": f"Cycle not found: {cycle_id}"}

    cycle = parse_cycle_file(cycle_path)
    current_phase = cycle["current_phase"]

    if not current_phase:
        return {"success": False, "error": "Could not determine current phase"}

    phase_data = cycle["phases"].get(current_phase.lower(), {})
    tasks = phase_data.get("tasks", [])

    # Validation rules per phase
    issues = []
    warnings = []

    if current_phase == "Focus":
        # Must have test scenarios
        test_task = any("test scenario" in t["description"].lower() for t in tasks if t["completed"])
        if not test_task:
            issues.append("MANDATORY: Test scenarios must be defined before advancing")

        # Should have architecture
        arch_task = any("architecture" in t["description"].lower() for t in tasks if t["completed"])
        if not arch_task:
            warnings.append("Architecture design not marked complete")

    elif current_phase == "Orchestrate":
        # Need minimum 3 tasks defined for next phase
        if phase_data["total"] < 3:
            issues.append(f"Need at least 3 tasks (have {phase_data['total']})")

    elif current_phase == "Refine":
        # Tests should be written
        test_task = any("test" in t["description"].lower() for t in tasks if t["completed"])
        if not test_task:
            issues.append("No tests marked as complete (TDD requires tests first)")

        # Code review
        review_task = any("review" in t["description"].lower() for t in tasks if t["completed"])
        if not review_task:
            warnings.append("Code review not marked complete")

    elif current_phase == "Generate":
        # Documentation
        doc_task = any("doc" in t["description"].lower() for t in tasks if t["completed"])
        if not doc_task:
            warnings.append("Documentation not marked complete")

    elif current_phase == "Evaluate":
        # Metrics
        if phase_data["completed"] < 1:
            warnings.append("No evaluation tasks completed")

    valid = len(issues) == 0

    return {
        "success": True,
        "cycle_id": cycle["id"],
        "feature": cycle["feature"],
        "current_phase": current_phase,
        "valid": valid,
        "can_advance": valid,
        "progress": phase_data["progress"],
        "completed_tasks": phase_data["completed"],
        "total_tasks": phase_data["total"],
        "issues": issues,
        "warnings": warnings
    }


def format_progress_bar(progress: int, width: int = 10) -> str:
    """Create a text progress bar."""
    filled = int(progress / 100 * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def main():
    parser = argparse.ArgumentParser(description="FORGE Status")
    parser.add_argument("cycle_id", nargs="?", help="Specific cycle ID")
    parser.add_argument("--all", "-a", action="store_true", help="Include completed cycles")
    parser.add_argument("--validate", "-v", action="store_true", help="Run checkpoint validation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        if args.validate:
            result = validate_checkpoint(args.cycle_id)
        else:
            result = get_status(args.cycle_id, args.all)
    except FileNotFoundError as e:
        result = {"success": False, "error": str(e)}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not result.get("success"):
            print(f"Error: {result.get('error')}", file=sys.stderr)
            sys.exit(1)

        if args.validate:
            # Checkpoint output
            status = "✓ PASS" if result["valid"] else "✗ FAIL"
            print(f"\n{'='*50}")
            print(f"FORGE Checkpoint: {result['feature']}")
            print(f"{'='*50}")
            print(f"Phase: {result['current_phase']} [{status}]")
            print(f"Progress: [{format_progress_bar(result['progress'])}] {result['progress']}%")
            print(f"Tasks: {result['completed_tasks']}/{result['total_tasks']}")

            if result["issues"]:
                print(f"\n❌ Blocking Issues:")
                for issue in result["issues"]:
                    print(f"   • {issue}")

            if result["warnings"]:
                print(f"\n⚠️  Warnings:")
                for warning in result["warnings"]:
                    print(f"   • {warning}")

            if result["can_advance"]:
                print(f"\n✓ Ready to advance to next phase")
            else:
                print(f"\n✗ Cannot advance - resolve issues first")
            print()

        else:
            # Status output
            if not result["cycles"]:
                print("No active cycles found.")
                print("Create one with: uv run forge_cycle.py new \"feature-name\"")
                return

            for cycle in result["cycles"]:
                completed_marker = " [COMPLETED]" if cycle.get("completed") else ""
                print(f"\n{'='*50}")
                print(f"📦 {cycle['feature']}{completed_marker}")
                print(f"{'='*50}")
                print(f"ID: {cycle['id']}")
                print(f"Priority: {cycle['priority']}")
                print(f"Overall: [{format_progress_bar(cycle['overall_progress'])}] {cycle['overall_progress']}%")
                print()

                for phase_name in PHASES:
                    phase = cycle["phases"].get(phase_name.lower(), {})
                    icon = PHASE_ICONS.get(phase_name, "")
                    status = phase.get("status", "Pending")
                    progress = phase.get("progress", 0)

                    status_marker = ""
                    if status == "Active":
                        status_marker = " ← CURRENT"
                    elif status == "Complete":
                        status_marker = " ✓"

                    bar = format_progress_bar(progress)
                    print(f"{icon} {phase_name:12} [{bar}] {progress:3}%{status_marker}")

                print()


if __name__ == "__main__":
    main()
