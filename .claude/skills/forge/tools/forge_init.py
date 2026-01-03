# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
FORGE Init Tool - Initialize .forge/ directory structure

Usage:
    uv run forge_init.py [--force]

Creates the .forge/ directory with:
- config.yaml - Project configuration
- learnings.md - Knowledge base
- cycles/active/ - Active development cycles
- cycles/completed/ - Archived cycles
- templates/ - Cycle templates
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml


def get_forge_dir() -> Path:
    """Get the .forge directory path in current working directory."""
    return Path.cwd() / ".forge"


def create_config(forge_dir: Path, project_name: str = None) -> dict:
    """Create default config.yaml content."""
    if not project_name:
        project_name = Path.cwd().name

    return {
        "project": project_name,
        "description": f"FORGE-managed project: {project_name}",
        "created": datetime.now().isoformat(),
        "version": "1.0.0",
        "settings": {
            "strict_validation": True,
            "require_test_scenarios": True,
            "auto_advance": False,
        },
        "phases": {
            "focus": {"enabled": True},
            "orchestrate": {"enabled": True},
            "refine": {"enabled": True},
            "generate": {"enabled": True},
            "evaluate": {"enabled": True},
        }
    }


def create_learnings_template() -> str:
    """Create initial learnings.md content."""
    return """# Project Learnings

Knowledge base for patterns, insights, and lessons learned.

## Categories

- **success**: Practices that worked well
- **failure**: Things to avoid
- **pattern**: Reusable solutions
- **antipattern**: Solutions to avoid
- **tool**: Tool recommendations
- **process**: Process improvements

## Learnings

<!-- Learnings will be added below -->

"""


def create_claude_md_section(project_name: str) -> str:
    """Create FORGE section for CLAUDE.md."""
    return f"""
## FORGE Integration

This project uses the **FORGE** development framework for structured, phase-based development.

### Before Any Development Work

Always check current FORGE status:
```bash
uv run .claude/skills/forge/tools/forge_status.py
```

### Phase-Appropriate Behavior

| Current Phase | Appropriate Work | Blocked Work |
|---------------|------------------|--------------|
| **Focus** | Requirements, test scenarios, architecture | Code implementation |
| **Orchestrate** | Task breakdown, planning, test strategy | Code implementation |
| **Refine** | TDD implementation (tests first!) | New features outside scope |
| **Generate** | Build, deployment, documentation | New features |
| **Evaluate** | Metrics, retrospective, learnings | New development |

### Key Rules

1. **No code without test scenarios** - Must be defined in Focus phase
2. **TDD in Refine** - Always write tests before implementation
3. **Respect phase gates** - Complete requirements before advancing
4. **Capture learnings** - Document insights for future cycles

### FORGE Commands

```bash
# Status and validation
uv run .claude/skills/forge/tools/forge_status.py
uv run .claude/skills/forge/tools/forge_status.py --validate

# Phase management
uv run .claude/skills/forge/tools/forge_phase.py advance
uv run .claude/skills/forge/tools/forge_phase.py complete-task "task name"

# Learnings
uv run .claude/skills/forge/tools/forge_learn.py add pattern "title" "description"
```

---
"""


def update_claude_md(project_name: str) -> tuple[Path, bool]:
    """Create or update CLAUDE.md with FORGE integration section."""
    claude_md_path = Path.cwd() / "CLAUDE.md"
    forge_section = create_claude_md_section(project_name)
    created_new = False

    if claude_md_path.exists():
        content = claude_md_path.read_text()
        if "## FORGE Integration" not in content:
            # Append FORGE section
            content = content.rstrip() + "\n" + forge_section
            claude_md_path.write_text(content)
    else:
        # Create new CLAUDE.md
        content = f"# {project_name}\n{forge_section}"
        claude_md_path.write_text(content)
        created_new = True

    return claude_md_path, created_new


def create_cycle_template() -> str:
    """Create cycle.md template content."""
    return """# Feature: {{FEATURE}}

**Created**: {{DATE}}
**Status**: Focus
**Priority**: {{PRIORITY}}

## Progress

### Phase 1: Focus [Active]
- [ ] Gather requirements
- [ ] Define test scenarios (MANDATORY)
- [ ] Design architecture
- [ ] Identify security risks
- [ ] Create/Update PRD

### Phase 2: Orchestrate [Pending]
- [ ] Break down tasks (minimum 3)
- [ ] Map dependencies
- [ ] Define test strategy
- [ ] Assign priorities

### Phase 3: Refine [Pending]
- [ ] Write tests first (RED)
- [ ] Implement code (GREEN)
- [ ] Refactor (REFACTOR)
- [ ] Code review completed
- [ ] All tests passing

### Phase 4: Generate [Pending]
- [ ] Build artifacts
- [ ] Update documentation
- [ ] Final validation
- [ ] Deployment prepared

### Phase 5: Evaluate [Pending]
- [ ] Collect success metrics
- [ ] Conduct retrospective
- [ ] Document learnings
- [ ] Archive cycle

## Notes

### Requirements
<!-- Requirements gathered during Focus phase -->

### Test Scenarios
<!-- MANDATORY: Define before any code -->

### Architecture Decisions
<!-- Design decisions and rationale -->

"""


def init_forge(force: bool = False, project_name: str = None) -> dict:
    """Initialize .forge/ directory structure."""
    forge_dir = get_forge_dir()

    # Check if already initialized
    if forge_dir.exists() and not force:
        return {
            "success": False,
            "error": f".forge/ already exists at {forge_dir}. Use --force to reinitialize.",
            "path": str(forge_dir)
        }

    # Create directory structure
    dirs = [
        forge_dir,
        forge_dir / "cycles" / "active",
        forge_dir / "cycles" / "completed",
        forge_dir / "templates",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Create config.yaml
    config = create_config(forge_dir, project_name)
    config_path = forge_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Create learnings.md
    learnings_path = forge_dir / "learnings.md"
    with open(learnings_path, "w") as f:
        f.write(create_learnings_template())

    # Create cycle template
    template_path = forge_dir / "templates" / "cycle.md"
    with open(template_path, "w") as f:
        f.write(create_cycle_template())

    # Update CLAUDE.md with FORGE integration
    claude_md_path, claude_created = update_claude_md(config["project"])

    files_created = [
        str(config_path),
        str(learnings_path),
        str(template_path),
    ]
    if claude_created:
        files_created.append(str(claude_md_path))

    return {
        "success": True,
        "message": "FORGE initialized successfully",
        "path": str(forge_dir),
        "created": {
            "directories": [str(d) for d in dirs],
            "files": files_created
        },
        "claude_md": {
            "path": str(claude_md_path),
            "created": claude_created,
            "updated": not claude_created
        },
        "config": config
    }


def main():
    parser = argparse.ArgumentParser(
        description="Initialize FORGE in current directory"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reinitialization if .forge/ exists"
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Project name (defaults to directory name)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()
    result = init_forge(force=args.force, project_name=args.name)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"FORGE initialized at {result['path']}")
            print(f"Project: {result['config']['project']}")
            print("\nCreated:")
            for f in result["created"]["files"]:
                print(f"  - {f}")

            # CLAUDE.md status
            claude_info = result.get("claude_md", {})
            if claude_info.get("created"):
                print(f"  - {claude_info['path']} (created)")
            elif claude_info.get("updated"):
                print(f"\nUpdated: {claude_info['path']} (added FORGE integration)")
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
