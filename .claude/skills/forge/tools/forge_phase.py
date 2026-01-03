# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
FORGE Phase Tool - Manage development cycle phases

Usage:
    uv run forge_phase.py advance [cycle-id] [--force]
    uv run forge_phase.py update [cycle-id] --task "task description"
    uv run forge_phase.py complete-task [cycle-id] "task description"
    uv run forge_phase.py validate [cycle-id]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


PHASES = ["Focus", "Orchestrate", "Refine", "Generate", "Evaluate"]

PHASE_REQUIREMENTS = {
    "Focus": {
        "mandatory": ["test scenarios"],
        "minimum_tasks": 1,
        "description": "Requirements, architecture, test scenarios"
    },
    "Orchestrate": {
        "mandatory": [],
        "minimum_tasks": 3,
        "description": "Task breakdown, dependencies, test strategy"
    },
    "Refine": {
        "mandatory": ["tests", "code review"],
        "minimum_tasks": 2,
        "description": "TDD implementation (RED-GREEN-REFACTOR)"
    },
    "Generate": {
        "mandatory": ["documentation"],
        "minimum_tasks": 1,
        "description": "Build artifacts, deployment prep"
    },
    "Evaluate": {
        "mandatory": [],
        "minimum_tasks": 1,
        "description": "Metrics, retrospective, learnings"
    }
}


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    forge_dir = Path.cwd() / ".forge"
    if not forge_dir.exists():
        raise FileNotFoundError(".forge/ not found. Run forge_init.py first.")
    return forge_dir


def find_active_cycle(cycle_id: str = None) -> Path:
    """Find active cycle file. If no ID provided, use the only active cycle."""
    forge_dir = get_forge_dir()
    active_dir = forge_dir / "cycles" / "active"

    if cycle_id:
        cycle_path = active_dir / f"{cycle_id}.md"
        if not cycle_path.exists():
            raise FileNotFoundError(f"Cycle '{cycle_id}' not found")
        return cycle_path

    # Find single active cycle
    cycles = list(active_dir.glob("*.md"))
    if len(cycles) == 0:
        raise FileNotFoundError("No active cycles found")
    if len(cycles) > 1:
        raise ValueError(f"Multiple active cycles found. Specify cycle_id: {[c.stem for c in cycles]}")
    return cycles[0]


def get_current_phase(content: str) -> tuple[str, int]:
    """Get the current active phase from cycle content."""
    for i, phase in enumerate(PHASES):
        if f"### Phase {i+1}: {phase} [Active]" in content:
            return phase, i
    return None, -1


def parse_phase_tasks(content: str, phase: str) -> list[dict]:
    """Parse tasks from a specific phase."""
    phase_idx = PHASES.index(phase) + 1
    pattern = rf'### Phase {phase_idx}: {phase} \[\w+\](.*?)(?=### Phase|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    tasks = []
    task_pattern = r'- \[([x ])\] (.+)$'
    for m in re.finditer(task_pattern, match.group(1), re.MULTILINE):
        tasks.append({
            "completed": m.group(1) == "x",
            "description": m.group(2).strip()
        })
    return tasks


def validate_phase(content: str, phase: str) -> dict:
    """Validate if phase requirements are met for advancement."""
    tasks = parse_phase_tasks(content, phase)
    requirements = PHASE_REQUIREMENTS[phase]

    completed = [t for t in tasks if t["completed"]]
    incomplete = [t for t in tasks if not t["completed"]]

    issues = []

    # Check minimum tasks completed
    if len(completed) < requirements["minimum_tasks"]:
        issues.append(f"Need at least {requirements['minimum_tasks']} tasks completed (have {len(completed)})")

    # Check mandatory items
    for mandatory in requirements["mandatory"]:
        found = any(mandatory.lower() in t["description"].lower() for t in completed)
        if not found:
            issues.append(f"MANDATORY: '{mandatory}' task not completed")

    return {
        "phase": phase,
        "valid": len(issues) == 0,
        "completed_tasks": len(completed),
        "total_tasks": len(tasks),
        "progress": round(len(completed) / len(tasks) * 100) if tasks else 0,
        "issues": issues,
        "requirements": requirements
    }


def advance_phase(cycle_id: str = None, force: bool = False) -> dict:
    """Advance cycle to the next phase."""
    cycle_path = find_active_cycle(cycle_id)
    content = cycle_path.read_text()

    current_phase, phase_idx = get_current_phase(content)
    if current_phase is None:
        return {"success": False, "error": "Could not determine current phase"}

    if phase_idx >= len(PHASES) - 1:
        return {
            "success": False,
            "error": f"Already at final phase ({current_phase}). Use forge_cycle.py complete to finish."
        }

    # Validate current phase
    validation = validate_phase(content, current_phase)
    if not validation["valid"] and not force:
        return {
            "success": False,
            "error": "Phase validation failed",
            "validation": validation,
            "hint": "Use --force to override validation"
        }

    next_phase = PHASES[phase_idx + 1]

    # Update content
    # Mark current phase as Complete
    content = content.replace(
        f"### Phase {phase_idx + 1}: {current_phase} [Active]",
        f"### Phase {phase_idx + 1}: {current_phase} [Complete]"
    )
    # Mark next phase as Active
    content = content.replace(
        f"### Phase {phase_idx + 2}: {next_phase} [Pending]",
        f"### Phase {phase_idx + 2}: {next_phase} [Active]"
    )
    # Update status
    content = re.sub(r'\*\*Status\*\*: .+', f'**Status**: {next_phase}', content)

    cycle_path.write_text(content)

    return {
        "success": True,
        "message": f"Advanced from {current_phase} to {next_phase}",
        "cycle_id": cycle_path.stem,
        "previous_phase": current_phase,
        "current_phase": next_phase,
        "validation": validation
    }


def complete_task(cycle_id: str, task_description: str) -> dict:
    """Mark a task as completed."""
    cycle_path = find_active_cycle(cycle_id)
    content = cycle_path.read_text()

    # Find and mark task as complete
    # Match partial task descriptions
    pattern = rf'- \[ \] ([^\n]*{re.escape(task_description)}[^\n]*)'
    match = re.search(pattern, content, re.IGNORECASE)

    if not match:
        return {
            "success": False,
            "error": f"Task not found: '{task_description}'",
            "hint": "Task may already be complete or description doesn't match"
        }

    full_task = match.group(1)
    content = content.replace(f"- [ ] {full_task}", f"- [x] {full_task}")

    cycle_path.write_text(content)

    return {
        "success": True,
        "message": f"Task completed: {full_task}",
        "cycle_id": cycle_path.stem
    }


def add_task(cycle_id: str, task_description: str, phase: str = None) -> dict:
    """Add a new task to current or specified phase."""
    cycle_path = find_active_cycle(cycle_id)
    content = cycle_path.read_text()

    if phase is None:
        phase, _ = get_current_phase(content)

    if phase not in PHASES:
        return {"success": False, "error": f"Invalid phase: {phase}"}

    phase_idx = PHASES.index(phase) + 1
    pattern = rf'(### Phase {phase_idx}: {phase} \[\w+\].*?)((?=### Phase|\Z))'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return {"success": False, "error": f"Phase {phase} not found in cycle"}

    phase_content = match.group(1)
    # Add task before the next section
    new_task = f"- [ ] {task_description}\n"

    # Find last task line and insert after
    last_task_match = list(re.finditer(r'- \[[x ]\] .+\n', phase_content))
    if last_task_match:
        insert_pos = last_task_match[-1].end()
        new_phase_content = phase_content[:insert_pos] + new_task + phase_content[insert_pos:]
    else:
        # No tasks yet, add after header
        header_match = re.search(r'### Phase .+\n', phase_content)
        if header_match:
            insert_pos = header_match.end()
            new_phase_content = phase_content[:insert_pos] + new_task + phase_content[insert_pos:]
        else:
            return {"success": False, "error": "Could not find insertion point"}

    content = content.replace(phase_content, new_phase_content)
    cycle_path.write_text(content)

    return {
        "success": True,
        "message": f"Task added to {phase}: {task_description}",
        "cycle_id": cycle_path.stem,
        "phase": phase
    }


def validate_cycle(cycle_id: str = None) -> dict:
    """Validate current phase of a cycle."""
    cycle_path = find_active_cycle(cycle_id)
    content = cycle_path.read_text()

    current_phase, _ = get_current_phase(content)
    if current_phase is None:
        return {"success": False, "error": "Could not determine current phase"}

    validation = validate_phase(content, current_phase)

    return {
        "success": True,
        "cycle_id": cycle_path.stem,
        "current_phase": current_phase,
        "validation": validation
    }


def main():
    parser = argparse.ArgumentParser(description="FORGE Phase Management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # advance command
    advance_parser = subparsers.add_parser("advance", help="Advance to next phase")
    advance_parser.add_argument("cycle_id", nargs="?", help="Cycle ID (optional if single active cycle)")
    advance_parser.add_argument("--force", "-f", action="store_true", help="Force advancement")

    # complete-task command
    task_parser = subparsers.add_parser("complete-task", help="Mark task as completed")
    task_parser.add_argument("cycle_id", nargs="?", help="Cycle ID")
    task_parser.add_argument("task", help="Task description (partial match)")

    # add-task command
    add_parser = subparsers.add_parser("add-task", help="Add new task")
    add_parser.add_argument("cycle_id", nargs="?", help="Cycle ID")
    add_parser.add_argument("task", help="Task description")
    add_parser.add_argument("--phase", "-p", choices=[p.lower() for p in PHASES], help="Target phase")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate current phase")
    validate_parser.add_argument("cycle_id", nargs="?", help="Cycle ID")

    # Global options
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        if args.command == "advance":
            result = advance_phase(args.cycle_id, args.force)
        elif args.command == "complete-task":
            result = complete_task(args.cycle_id, args.task)
        elif args.command == "add-task":
            phase = args.phase.capitalize() if args.phase else None
            result = add_task(args.cycle_id, args.task, phase)
        elif args.command == "validate":
            result = validate_cycle(args.cycle_id)
        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}
    except (FileNotFoundError, ValueError) as e:
        result = {"success": False, "error": str(e)}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            if args.command == "advance":
                print(f"Advanced: {result['previous_phase']} -> {result['current_phase']}")
                v = result["validation"]
                print(f"Previous phase: {v['completed_tasks']}/{v['total_tasks']} tasks ({v['progress']}%)")
            elif args.command == "complete-task":
                print(f"Completed: {result['message']}")
            elif args.command == "add-task":
                print(f"Added: {result['message']}")
            elif args.command == "validate":
                v = result["validation"]
                status = "PASS" if v["valid"] else "FAIL"
                print(f"Phase: {result['current_phase']} [{status}]")
                print(f"Progress: {v['completed_tasks']}/{v['total_tasks']} ({v['progress']}%)")
                if v["issues"]:
                    print("\nIssues:")
                    for issue in v["issues"]:
                        print(f"  - {issue}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            if "validation" in result:
                v = result["validation"]
                if v.get("issues"):
                    print("\nValidation issues:", file=sys.stderr)
                    for issue in v["issues"]:
                        print(f"  - {issue}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
