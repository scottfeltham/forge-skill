# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
FORGE Learn Tool - Manage learnings and retrospectives

Usage:
    uv run forge_learn.py add <category> "title" "description"
    uv run forge_learn.py list [--category success]
    uv run forge_learn.py retro [cycle-id]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


CATEGORIES = ["success", "failure", "pattern", "antipattern", "tool", "process"]
CATEGORY_ICONS = {
    "success": "✅",
    "failure": "❌",
    "pattern": "🔄",
    "antipattern": "⚠️",
    "tool": "🔧",
    "process": "📋"
}


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    forge_dir = Path.cwd() / ".forge"
    if not forge_dir.exists():
        raise FileNotFoundError(".forge/ not found. Run forge_init.py first.")
    return forge_dir


def add_learning(category: str, title: str, description: str, context: str = None) -> dict:
    """Add a new learning to the knowledge base."""
    if category not in CATEGORIES:
        return {
            "success": False,
            "error": f"Invalid category '{category}'. Must be one of: {CATEGORIES}"
        }

    forge_dir = get_forge_dir()
    learnings_path = forge_dir / "learnings.md"

    # Create if doesn't exist
    if not learnings_path.exists():
        learnings_path.write_text("""# Project Learnings

## Learnings

""")

    content = learnings_path.read_text()

    # Format new learning
    timestamp = datetime.now().strftime("%Y-%m-%d")
    icon = CATEGORY_ICONS.get(category, "📝")

    learning_entry = f"""
### {icon} {title}
**Category**: {category}
**Date**: {timestamp}

{description}
"""
    if context:
        learning_entry += f"\n**Context**: {context}\n"

    learning_entry += "\n---\n"

    # Append to learnings section
    if "## Learnings" in content:
        content = content.replace("## Learnings\n", f"## Learnings\n{learning_entry}")
    else:
        content += f"\n## Learnings\n{learning_entry}"

    learnings_path.write_text(content)

    return {
        "success": True,
        "message": f"Learning added: {title}",
        "category": category,
        "title": title,
        "path": str(learnings_path)
    }


def list_learnings(category: str = None) -> dict:
    """List all learnings, optionally filtered by category."""
    forge_dir = get_forge_dir()
    learnings_path = forge_dir / "learnings.md"

    if not learnings_path.exists():
        return {"success": True, "count": 0, "learnings": []}

    content = learnings_path.read_text()

    # Parse learnings
    learnings = []
    pattern = r'### ([^\n]+)\n\*\*Category\*\*: (\w+)\n\*\*Date\*\*: ([^\n]+)\n\n(.*?)(?=\n---|\Z)'

    for match in re.finditer(pattern, content, re.DOTALL):
        title_with_icon = match.group(1)
        # Remove icon from title
        title = re.sub(r'^[^\w\s]+\s*', '', title_with_icon).strip()
        cat = match.group(2)
        date = match.group(3)
        desc = match.group(4).strip()

        # Extract context if present
        context = None
        context_match = re.search(r'\*\*Context\*\*: (.+)', desc)
        if context_match:
            context = context_match.group(1)
            desc = re.sub(r'\n?\*\*Context\*\*: .+', '', desc).strip()

        if category is None or cat == category:
            learnings.append({
                "title": title,
                "category": cat,
                "date": date,
                "description": desc,
                "context": context
            })

    return {
        "success": True,
        "count": len(learnings),
        "learnings": learnings
    }


def run_retrospective(cycle_id: str = None) -> dict:
    """Generate a retrospective for a cycle."""
    forge_dir = get_forge_dir()

    # Find cycle
    if cycle_id:
        # Check active then completed
        cycle_path = forge_dir / "cycles" / "active" / f"{cycle_id}.md"
        if not cycle_path.exists():
            cycle_path = forge_dir / "cycles" / "completed" / f"{cycle_id}.md"
    else:
        # Use most recent active cycle
        active_dir = forge_dir / "cycles" / "active"
        cycles = list(active_dir.glob("*.md"))
        if not cycles:
            return {"success": False, "error": "No active cycles found"}
        cycle_path = cycles[0]

    if not cycle_path.exists():
        return {"success": False, "error": f"Cycle not found: {cycle_id}"}

    content = cycle_path.read_text()

    # Parse cycle data
    feature_match = re.search(r'^# Feature: (.+)$', content, re.MULTILINE)
    feature = feature_match.group(1) if feature_match else "Unknown"

    created_match = re.search(r'\*\*Created\*\*: (.+)$', content, re.MULTILINE)
    created = created_match.group(1) if created_match else "Unknown"

    # Count tasks per phase
    phases_data = {}
    phase_names = ["Focus", "Orchestrate", "Refine", "Generate", "Evaluate"]

    total_completed = 0
    total_tasks = 0

    for i, phase in enumerate(phase_names):
        pattern = rf'### Phase {i+1}: {phase} \[(\w+)\](.*?)(?=### Phase|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            status = match.group(1)
            tasks_content = match.group(2)
            completed = len(re.findall(r'- \[x\]', tasks_content))
            total = len(re.findall(r'- \[[ x]\]', tasks_content))
            phases_data[phase] = {
                "status": status,
                "completed": completed,
                "total": total
            }
            total_completed += completed
            total_tasks += total

    # Generate retrospective
    retro = {
        "cycle_id": cycle_path.stem,
        "feature": feature,
        "created": created,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_tasks": total_tasks,
            "completed_tasks": total_completed,
            "completion_rate": round(total_completed / total_tasks * 100) if total_tasks > 0 else 0
        },
        "phases": phases_data,
        "prompts": {
            "what_went_well": "What practices, tools, or approaches worked well in this cycle?",
            "what_could_improve": "What challenges did you face? What would you do differently?",
            "action_items": "What specific improvements will you make in the next cycle?",
            "learnings": "What key insights should be captured for future reference?"
        }
    }

    return {
        "success": True,
        "retrospective": retro
    }


def main():
    parser = argparse.ArgumentParser(description="FORGE Learnings Management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a learning")
    add_parser.add_argument("category", choices=CATEGORIES, help="Learning category")
    add_parser.add_argument("title", help="Learning title")
    add_parser.add_argument("description", help="Detailed description")
    add_parser.add_argument("--context", "-c", help="When/where this applies")

    # list command
    list_parser = subparsers.add_parser("list", help="List learnings")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")

    # retro command
    retro_parser = subparsers.add_parser("retro", help="Run retrospective")
    retro_parser.add_argument("cycle_id", nargs="?", help="Cycle ID")

    # Global options
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        if args.command == "add":
            result = add_learning(args.category, args.title, args.description, args.context)
        elif args.command == "list":
            result = list_learnings(args.category)
        elif args.command == "retro":
            result = run_retrospective(args.cycle_id)
        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}
    except FileNotFoundError as e:
        result = {"success": False, "error": str(e)}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not result.get("success"):
            print(f"Error: {result.get('error')}", file=sys.stderr)
            sys.exit(1)

        if args.command == "add":
            icon = CATEGORY_ICONS.get(result["category"], "📝")
            print(f"{icon} Learning added: {result['title']}")

        elif args.command == "list":
            if result["count"] == 0:
                print("No learnings found.")
                print("Add one with: uv run forge_learn.py add <category> \"title\" \"description\"")
            else:
                print(f"\n📚 Learnings ({result['count']} total)\n")
                for learning in result["learnings"]:
                    icon = CATEGORY_ICONS.get(learning["category"], "📝")
                    print(f"{icon} [{learning['category']}] {learning['title']}")
                    print(f"   {learning['description'][:80]}...")
                    print()

        elif args.command == "retro":
            r = result["retrospective"]
            print(f"\n{'='*50}")
            print(f"📊 RETROSPECTIVE: {r['feature']}")
            print(f"{'='*50}")
            print(f"Cycle: {r['cycle_id']}")
            print(f"Started: {r['created']}")
            print(f"Completion: {r['summary']['completion_rate']}% ({r['summary']['completed_tasks']}/{r['summary']['total_tasks']} tasks)")
            print()

            print("Phase Summary:")
            for phase, data in r["phases"].items():
                status_icon = "✓" if data["status"] == "Complete" else "○"
                print(f"  {status_icon} {phase}: {data['completed']}/{data['total']} tasks")
            print()

            print("Reflection Prompts:")
            for key, prompt in r["prompts"].items():
                print(f"\n  📝 {prompt}")
            print()


if __name__ == "__main__":
    main()
