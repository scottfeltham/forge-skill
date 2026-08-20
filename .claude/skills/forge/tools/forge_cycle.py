#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Manage FORGE development cycles."""

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

CYCLE_TEMPLATE = """# Cycle: {name}

**Created**: {created}
**Priority**: {priority}
**Status**: Active

## Overview

<!-- Describe what this cycle aims to accomplish -->

---

<!-- FORGE_PHASE:Focus:Active -->
## Phase 1: Focus

**Purpose**: Define what you're building and why.

### Required Outputs
- [ ] Problem statement and target users defined
- [ ] Testable success criteria written
- [ ] System Context diagram (C4 L1) created
- [ ] Clear boundaries on what you WON'T build

### Notes

<!-- Document Focus phase work here -->

---

<!-- FORGE_PHASE:Orchestrate:Pending -->
## Phase 2: Orchestrate

**Purpose**: Break the work into session-sized pieces.

### Required Outputs
- [ ] Container architecture (C4 L2) designed
- [ ] Component architecture (C4 L3) designed
- [ ] Dependency map created
- [ ] Tasks sized for single AI sessions

### Tasks

<!-- List tasks here -->

---

<!-- FORGE_PHASE:Refine:Pending -->
## Phase 3: Refine

**Purpose**: Define exactly what "done" looks like.

### Required Outputs
- [ ] Acceptance criteria in Given-When-Then format
- [ ] Interface specifications documented
- [ ] Edge cases enumerated by category
- [ ] Constraints vs criteria documented

**CRITICAL**: No code in this phase - specifications only.

### Specifications

<!-- Document specifications here -->

---

<!-- FORGE_PHASE:Generate:Pending -->
## Phase 4: Generate

**Purpose**: AI writes code following TDD.

### Process
- [ ] RED: Write failing tests
- [ ] GREEN: Minimal code to pass
- [ ] REFACTOR: Improve while green
- [ ] Code review: Linter and type checks pass
- [ ] Code review: TDD compliance verified
- [ ] Code review: Acceptance criteria alignment checked

### Implementation Notes

<!-- Document implementation progress here -->

---

<!-- FORGE_PHASE:Evaluate:Pending -->
## Phase 5: Evaluate

**Purpose**: Verify output matches intent.

### Checklist
- [ ] Criteria verified line-by-line
- [ ] Edge cases tested
- [ ] Code review: Full test suite passes with coverage threshold met
- [ ] Code review: Security review completed
- [ ] Code review: Integration and interface contracts verified
- [ ] Cycle review summary emitted (docs/<cycle>/cycle-review.md + HTML sibling)
- [ ] Disposition decision made

### Disposition

<!-- Accept / Accept with issues / Revise / Reject -->

---

## Learnings

<!-- Capture learnings during and after the cycle -->
"""

HIL_CYCLE_TEMPLATE = """# Cycle: {name}

**Created**: {created}
**Priority**: {priority}
**Status**: Active
**Mode**: HIL (Human-in-the-Loop)

## Overview

<!-- Describe the change/update this iteration addresses -->

---

<!-- FORGE_PHASE:Refine:Active -->
## Phase 1: Refine

**Purpose**: Define exactly what "done" looks like for this change.

### Required Outputs
- [ ] Acceptance criteria in Given-When-Then format
- [ ] Interface changes documented (if any)
- [ ] Edge cases enumerated
- [ ] Constraints vs criteria documented

**CRITICAL**: No code in this phase - specifications only.

### Specifications

<!-- Document specifications here -->

---

<!-- FORGE_PHASE:Generate:Pending -->
## Phase 2: Generate

**Purpose**: Implement the change following TDD.

### Process
- [ ] RED: Write failing tests
- [ ] GREEN: Minimal code to pass
- [ ] REFACTOR: Improve while green
- [ ] Code review: Linter and type checks pass
- [ ] Code review: TDD compliance verified
- [ ] Code review: Acceptance criteria alignment checked

### Implementation Notes

<!-- Document implementation progress here -->

---

<!-- FORGE_PHASE:Evaluate:Pending -->
## Phase 3: Evaluate

**Purpose**: Verify output matches intent.

### Checklist
- [ ] Criteria verified line-by-line
- [ ] Edge cases tested
- [ ] Code review: Full test suite passes with coverage threshold met
- [ ] Code review: Security review completed
- [ ] Code review: Integration and interface contracts verified
- [ ] Cycle review summary emitted (docs/<cycle>/cycle-review.md + HTML sibling)
- [ ] Disposition decision made

### Disposition

<!-- Accept / Accept with issues / Revise / Reject -->

---

## Learnings

<!-- Capture learnings during and after the cycle -->
"""


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    return Path.cwd() / ".forge"


def slugify(name: str) -> str:
    """Convert name to slug for filename."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def new_cycle(name: str, priority: str = "medium", mode: str = "full") -> bool:
    """Create a new development cycle."""
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("Error: FORGE not initialized. Run forge_init.py first.")
        return False

    # Generate cycle ID and filename
    timestamp = datetime.now(timezone.utc)
    date_prefix = timestamp.strftime("%Y%m%d")
    slug = slugify(name)
    if not slug:
        print("Error: Cycle name must contain at least one letter or digit.")
        return False
    cycle_id = f"{date_prefix}-{slug}"
    filename = f"{cycle_id}.md"

    # Check for existing cycle with same name
    active_dir = forge_dir / "cycles" / "active"
    cycle_path = active_dir / filename

    if cycle_path.exists():
        print(f"Error: Cycle already exists: {cycle_path}")
        return False

    # Select template based on mode
    template = HIL_CYCLE_TEMPLATE if mode == "hil" else CYCLE_TEMPLATE
    content = template.format(
        name=name,
        created=timestamp.isoformat(),
        priority=priority,
    )

    with open(cycle_path, "w") as f:
        f.write(content)

    start_phase = "Refine" if mode == "hil" else "Focus"
    print(f"Created cycle: {cycle_id}")
    print(f"  File: {cycle_path}")
    print(f"  Mode: {'HIL (Human-in-the-Loop)' if mode == 'hil' else 'Full'}")
    print(f"  Phase: {start_phase} (Active)")
    print()

    if mode == "hil":
        print("HIL mode: Refine → Generate → Evaluate")
        print()
        print("Next steps:")
        print("  1. Write acceptance criteria (Given-When-Then)")
        print("  2. Document interface changes")
        print("  3. Enumerate edge cases")
        print("  4. Document constraints vs criteria")
    else:
        print("Next steps:")
        print("  1. Define problem statement and target users")
        print("  2. Write testable success criteria")
        print("  3. Create C4 L1 System Context diagram")
        print("  4. Set clear boundaries")
    print()
    print("Check status: uv run forge_status.py")

    return True


def list_cycles() -> None:
    """List all active and completed cycles."""
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("Error: FORGE not initialized. Run forge_init.py first.")
        return

    active_dir = forge_dir / "cycles" / "active"
    completed_dir = forge_dir / "cycles" / "completed"

    print("FORGE Cycles")
    print("=" * 40)

    # Active cycles
    print("\nActive:")
    active_cycles = sorted(active_dir.glob("*.md"))
    if active_cycles:
        for cycle in active_cycles:
            cycle_id = cycle.stem
            # Read to get current phase
            content = cycle.read_text()
            phase = _get_active_phase(content)
            print(f"  - {cycle_id} [{phase}]")
    else:
        print("  (none)")

    # Completed cycles
    print("\nCompleted:")
    completed_cycles = sorted(completed_dir.glob("*.md"))
    if completed_cycles:
        for cycle in completed_cycles:
            cycle_id = cycle.stem
            print(f"  - {cycle_id}")
    else:
        print("  (none)")


def _get_active_phase(content: str) -> str:
    """Extract the active phase from cycle content."""
    pattern = r"<!-- FORGE_PHASE:(\w+):Active -->"
    match = re.search(pattern, content)
    return match.group(1) if match else "Unknown"


def complete_cycle(cycle_id: str) -> bool:
    """Complete and archive a cycle."""
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("Error: FORGE not initialized.")
        return False

    active_dir = forge_dir / "cycles" / "active"
    completed_dir = forge_dir / "cycles" / "completed"

    # Find the cycle file
    cycle_path = None
    for path in active_dir.glob("*.md"):
        if cycle_id in path.stem:
            cycle_path = path
            break

    if not cycle_path:
        print(f"Error: Cycle not found: {cycle_id}")
        print("Available cycles:")
        for path in active_dir.glob("*.md"):
            print(f"  - {path.stem}")
        return False

    # Check if in Evaluate phase
    content = cycle_path.read_text()
    active_phase = _get_active_phase(content)

    if active_phase != "Evaluate":
        print(f"Error: Cycle is in {active_phase} phase, not Evaluate.")
        print("Complete all phases before finishing the cycle.")
        return False

    # Move to completed
    dest_path = completed_dir / cycle_path.name
    shutil.move(str(cycle_path), str(dest_path))

    print(f"Completed cycle: {cycle_path.stem}")
    print(f"  Archived to: {dest_path}")
    print()
    print("Consider running a retrospective: uv run forge_learn.py retro")

    return True


def abandon_cycle(cycle_id: str, reason: str) -> bool:
    """Abandon a cycle whose charter no longer describes the work.

    `complete` is NOT this verb and must not stand in for it. It takes no
    reason, requires the Evaluate phase, and records a completion — so reaching
    for it on superseded work writes a success that never happened into the one
    file a human reads to find out what did.

    Rewriting a charter is ordinary. When its outcome ids change it is a
    different promise, and the cycle opened for the old one can be neither
    finished nor resumed: its cached phases cite outcomes that no longer exist.
    Abandoning is the honest third option, and the reason is required because a
    cycle that stops without one tells the next person nothing.

    Abandoned cycles archive to `cycles/abandoned/`, not `cycles/completed/`, so
    that "completed" never has to be read with an asterisk.
    """
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("Error: FORGE not initialized.")
        return False

    if not reason.strip():
        print("Error: abandoning a cycle requires a reason.")
        return False

    active_dir = forge_dir / "cycles" / "active"
    abandoned_dir = forge_dir / "cycles" / "abandoned"

    cycle_path = None
    for path in active_dir.glob("*.md"):
        if cycle_id in path.stem:
            cycle_path = path
            break

    if not cycle_path:
        print(f"Error: Cycle not found: {cycle_id}")
        print("Available cycles:")
        for path in active_dir.glob("*.md"):
            print(f"  - {path.stem}")
        return False

    # Stamp the truth into the file before moving it. Any phase is valid here —
    # abandoning half-finished work is the case this exists for.
    content = cycle_path.read_text()
    reached = _get_active_phase(content)
    content = content.replace("**Status**: Active",
                              "**Status**: Abandoned", 1)
    content += (f"\n\n---\n\n## Abandoned\n\n"
                f"Reached **{reached}**, then abandoned.\n\n"
                f"**Reason**: {reason.strip()}\n")

    abandoned_dir.mkdir(parents=True, exist_ok=True)
    dest_path = abandoned_dir / cycle_path.name
    dest_path.write_text(content)
    cycle_path.unlink()

    print(f"Abandoned cycle: {cycle_path.stem}")
    print(f"  Reached: {reached}")
    print(f"  Reason: {reason.strip()}")
    print(f"  Archived to: {dest_path}")

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage FORGE development cycles")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # new command
    new_parser = subparsers.add_parser("new", help="Create a new cycle")
    new_parser.add_argument("name", help="Cycle name/description")
    new_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Cycle priority (default: medium)",
    )
    new_parser.add_argument(
        "--mode",
        choices=["full", "hil"],
        default="full",
        help="Cycle mode: full (all 5 phases) or hil (Refine-Generate-Evaluate only)",
    )

    # list command
    subparsers.add_parser("list", help="List all cycles")

    # complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a cycle")
    complete_parser.add_argument("cycle_id", help="Cycle ID to complete")

    abandon_parser = subparsers.add_parser(
        "abandon", help="Abandon a cycle whose charter no longer describes the work")
    abandon_parser.add_argument("cycle_id", help="Cycle ID to abandon")
    abandon_parser.add_argument(
        "--reason", required=True,
        help="Why. Required — a cycle that stops without one tells the next person nothing.")

    args = parser.parse_args()

    if args.command == "abandon":
        return 0 if abandon_cycle(args.cycle_id, args.reason) else 1
    if args.command == "new":
        success = new_cycle(args.name, args.priority, args.mode)
        return 0 if success else 1
    elif args.command == "list":
        list_cycles()
        return 0
    elif args.command == "complete":
        success = complete_cycle(args.cycle_id)
        return 0 if success else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
