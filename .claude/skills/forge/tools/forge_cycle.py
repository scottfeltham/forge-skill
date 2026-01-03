# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
FORGE Cycle Tool - Create and manage development cycles

Usage:
    uv run forge_cycle.py new "feature-name" [--priority high]
    uv run forge_cycle.py list [--all]
    uv run forge_cycle.py complete <cycle-id> [--notes "completion notes"]
    uv run forge_cycle.py show <cycle-id>
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    forge_dir = Path.cwd() / ".forge"
    if not forge_dir.exists():
        raise FileNotFoundError(".forge/ not found. Run forge_init.py first.")
    return forge_dir


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50]


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

    # Count completed tasks per phase
    phases = {}
    phase_names = ["Focus", "Orchestrate", "Refine", "Generate", "Evaluate"]

    for phase in phase_names:
        phase_pattern = rf'### Phase \d+: {phase} \[(\w+)\](.*?)(?=### Phase|\Z)'
        phase_match = re.search(phase_pattern, content, re.DOTALL)
        if phase_match:
            status = phase_match.group(1)
            tasks_content = phase_match.group(2)
            completed = len(re.findall(r'- \[x\]', tasks_content))
            total = len(re.findall(r'- \[[ x]\]', tasks_content))
            phases[phase.lower()] = {
                "status": status,
                "completed": completed,
                "total": total,
                "progress": round(completed / total * 100) if total > 0 else 0
            }

    return {
        "id": path.stem,
        "feature": feature,
        "created": created_match.group(1) if created_match else None,
        "status": status_match.group(1) if status_match else "Focus",
        "priority": priority_match.group(1) if priority_match else "medium",
        "phases": phases,
        "path": str(path)
    }


def new_cycle(feature: str, priority: str = "medium", description: str = None) -> dict:
    """Create a new development cycle."""
    forge_dir = get_forge_dir()

    # Generate cycle ID
    cycle_id = slugify(feature)
    timestamp = datetime.now().strftime("%Y%m%d")
    cycle_id = f"{cycle_id}-{timestamp}"

    # Check if cycle exists
    cycle_path = forge_dir / "cycles" / "active" / f"{cycle_id}.md"
    if cycle_path.exists():
        return {
            "success": False,
            "error": f"Cycle '{cycle_id}' already exists",
            "path": str(cycle_path)
        }

    # Load template
    template_path = forge_dir / "templates" / "cycle.md"
    if template_path.exists():
        template = template_path.read_text()
    else:
        # Fallback template
        template = """# Feature: {{FEATURE}}

**Created**: {{DATE}}
**Status**: Focus
**Priority**: {{PRIORITY}}

## Progress

### Phase 1: Focus [Active]
- [ ] Gather requirements
- [ ] Define test scenarios (MANDATORY)
- [ ] Design architecture
- [ ] Identify security risks

### Phase 2: Orchestrate [Pending]
- [ ] Break down tasks
- [ ] Map dependencies
- [ ] Define test strategy

### Phase 3: Refine [Pending]
- [ ] Write tests first
- [ ] Implement code
- [ ] Code review

### Phase 4: Generate [Pending]
- [ ] Build artifacts
- [ ] Update documentation

### Phase 5: Evaluate [Pending]
- [ ] Collect metrics
- [ ] Retrospective

## Notes

"""

    # Fill template
    content = template.replace("{{FEATURE}}", feature)
    content = content.replace("{{DATE}}", datetime.now().isoformat())
    content = content.replace("{{PRIORITY}}", priority)

    # Add description if provided
    if description:
        content = content.replace("## Notes\n", f"## Notes\n\n### Description\n{description}\n")

    # Write cycle file
    cycle_path.write_text(content)

    return {
        "success": True,
        "message": f"Cycle '{feature}' created",
        "cycle_id": cycle_id,
        "path": str(cycle_path),
        "phase": "Focus",
        "priority": priority
    }


def list_cycles(include_completed: bool = False) -> dict:
    """List all development cycles."""
    forge_dir = get_forge_dir()

    cycles = []

    # Get active cycles
    active_dir = forge_dir / "cycles" / "active"
    if active_dir.exists():
        for path in active_dir.glob("*.md"):
            cycle = parse_cycle_file(path)
            cycle["active"] = True
            cycles.append(cycle)

    # Get completed cycles if requested
    if include_completed:
        completed_dir = forge_dir / "cycles" / "completed"
        if completed_dir.exists():
            for path in completed_dir.glob("*.md"):
                cycle = parse_cycle_file(path)
                cycle["active"] = False
                cycles.append(cycle)

    return {
        "success": True,
        "count": len(cycles),
        "active_count": len([c for c in cycles if c.get("active")]),
        "cycles": cycles
    }


def show_cycle(cycle_id: str) -> dict:
    """Show details of a specific cycle."""
    forge_dir = get_forge_dir()

    # Look in active first, then completed
    for subdir in ["active", "completed"]:
        cycle_path = forge_dir / "cycles" / subdir / f"{cycle_id}.md"
        if cycle_path.exists():
            cycle = parse_cycle_file(cycle_path)
            cycle["content"] = cycle_path.read_text()
            return {"success": True, "cycle": cycle}

    return {
        "success": False,
        "error": f"Cycle '{cycle_id}' not found"
    }


def complete_cycle(cycle_id: str, notes: str = None, force: bool = False) -> dict:
    """Complete and archive a cycle."""
    forge_dir = get_forge_dir()

    active_path = forge_dir / "cycles" / "active" / f"{cycle_id}.md"
    if not active_path.exists():
        return {
            "success": False,
            "error": f"Active cycle '{cycle_id}' not found"
        }

    # Parse and validate
    cycle = parse_cycle_file(active_path)

    # Check if Evaluate phase is complete (unless forced)
    if not force:
        eval_phase = cycle["phases"].get("evaluate", {})
        if eval_phase.get("status") != "Complete" and eval_phase.get("progress", 0) < 100:
            return {
                "success": False,
                "error": "Evaluate phase not complete. Use --force to override.",
                "phase_status": eval_phase
            }

    # Read content and add completion notes
    content = active_path.read_text()
    completion_timestamp = datetime.now().isoformat()

    # Add completion section
    completion_section = f"""
## Completion

**Completed**: {completion_timestamp}
"""
    if notes:
        completion_section += f"**Notes**: {notes}\n"

    content += completion_section

    # Update status in content
    content = re.sub(r'\*\*Status\*\*: .+', '**Status**: Completed', content)

    # Move to completed
    completed_path = forge_dir / "cycles" / "completed" / f"{cycle_id}.md"
    completed_path.write_text(content)
    active_path.unlink()

    return {
        "success": True,
        "message": f"Cycle '{cycle_id}' completed and archived",
        "cycle_id": cycle_id,
        "completed_at": completion_timestamp,
        "path": str(completed_path)
    }


def main():
    parser = argparse.ArgumentParser(description="FORGE Cycle Management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new command
    new_parser = subparsers.add_parser("new", help="Create new cycle")
    new_parser.add_argument("feature", help="Feature name")
    new_parser.add_argument("--priority", "-p", default="medium",
                           choices=["low", "medium", "high", "critical"])
    new_parser.add_argument("--description", "-d", help="Feature description")

    # list command
    list_parser = subparsers.add_parser("list", help="List cycles")
    list_parser.add_argument("--all", "-a", action="store_true",
                            help="Include completed cycles")

    # show command
    show_parser = subparsers.add_parser("show", help="Show cycle details")
    show_parser.add_argument("cycle_id", help="Cycle ID")

    # complete command
    complete_parser = subparsers.add_parser("complete", help="Complete cycle")
    complete_parser.add_argument("cycle_id", help="Cycle ID")
    complete_parser.add_argument("--notes", "-n", help="Completion notes")
    complete_parser.add_argument("--force", "-f", action="store_true",
                                help="Force completion")

    # Global options
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        if args.command == "new":
            result = new_cycle(args.feature, args.priority, args.description)
        elif args.command == "list":
            result = list_cycles(args.all)
        elif args.command == "show":
            result = show_cycle(args.cycle_id)
        elif args.command == "complete":
            result = complete_cycle(args.cycle_id, args.notes, args.force)
        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}
    except FileNotFoundError as e:
        result = {"success": False, "error": str(e)}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            if args.command == "new":
                print(f"Created cycle: {result['cycle_id']}")
                print(f"Phase: {result['phase']}")
                print(f"Path: {result['path']}")
            elif args.command == "list":
                print(f"Cycles ({result['count']} total, {result['active_count']} active):\n")
                for c in result["cycles"]:
                    status = "active" if c.get("active") else "completed"
                    print(f"  [{status}] {c['id']}: {c['feature']} ({c['status']})")
            elif args.command == "show":
                c = result["cycle"]
                print(f"Cycle: {c['feature']}")
                print(f"Status: {c['status']}")
                print(f"Priority: {c['priority']}")
                print("\nPhase Progress:")
                for name, phase in c["phases"].items():
                    bar = "=" * (phase["progress"] // 10) + "-" * (10 - phase["progress"] // 10)
                    print(f"  {name.capitalize():12} [{bar}] {phase['progress']}%")
            elif args.command == "complete":
                print(f"Completed: {result['cycle_id']}")
                print(f"Archived to: {result['path']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
