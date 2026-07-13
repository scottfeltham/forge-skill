#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Check FORGE status and validate phase requirements."""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ALL_PHASES = ["Focus", "Orchestrate", "Refine", "Generate", "Evaluate"]


def get_cycle_phases(content: str) -> list[str]:
    """Extract the ordered list of phases present in a cycle file."""
    pattern = r"<!-- FORGE_PHASE:(\w+):\w+ -->"
    found = re.findall(pattern, content)
    return [p for p in ALL_PHASES if p in found]


@dataclass
class PhaseStatus:
    """Status of a single phase."""

    name: str
    state: str  # Active, Complete, Pending
    total_items: int
    completed_items: int
    items: list[tuple[bool, str]]  # (completed, text)

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100


@dataclass
class CycleStatus:
    """Status of a development cycle."""

    cycle_id: str
    path: Path
    active_phase: str
    phases: dict[str, PhaseStatus]


def get_forge_dir() -> Path:
    """Get the .forge directory path."""
    return Path.cwd() / ".forge"


def parse_cycle(path: Path) -> CycleStatus:
    """Parse a cycle file and extract status."""
    content = path.read_text()
    cycle_id = path.stem

    phases = {}
    active_phase = None
    cycle_phases = get_cycle_phases(content)

    # Parse each phase
    for phase_name in cycle_phases:
        # Find phase marker
        marker_pattern = rf"<!-- FORGE_PHASE:{phase_name}:(\w+) -->"
        marker_match = re.search(marker_pattern, content)

        if not marker_match:
            state = "Pending"
        else:
            state = marker_match.group(1)
            if state == "Active":
                active_phase = phase_name

        # Find phase section and extract checkboxes
        section_pattern = rf"## Phase \d+: {phase_name}.*?(?=## Phase \d+:|---\s*$|\Z)"
        section_match = re.search(section_pattern, content, re.DOTALL)

        items = []
        if section_match:
            section = section_match.group(0)
            # Find all checkboxes
            checkbox_pattern = r"- \[([ xX])\] (.+?)(?:\n|$)"
            for match in re.finditer(checkbox_pattern, section):
                completed = match.group(1).lower() == "x"
                text = match.group(2).strip()
                items.append((completed, text))

        total_items = len(items)
        completed_items = sum(1 for completed, _ in items if completed)

        phases[phase_name] = PhaseStatus(
            name=phase_name,
            state=state,
            total_items=total_items,
            completed_items=completed_items,
            items=items,
        )

    return CycleStatus(
        cycle_id=cycle_id,
        path=path,
        active_phase=active_phase or cycle_phases[0],
        phases=phases,
    )


def get_active_cycles() -> list[CycleStatus]:
    """Get all active cycles."""
    forge_dir = get_forge_dir()
    active_dir = forge_dir / "cycles" / "active"

    if not active_dir.exists():
        return []

    cycles = []
    for path in sorted(active_dir.glob("*.md")):
        cycles.append(parse_cycle(path))

    return cycles


def print_status(detailed: bool = False) -> None:
    """Print current FORGE status."""
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("FORGE not initialized. Run forge_init.py first.")
        return

    cycles = get_active_cycles()

    if not cycles:
        print("No active cycles.")
        print("Start one with: uv run forge_cycle.py new \"feature-name\"")
        return

    print("FORGE Status")
    print("=" * 50)

    for cycle in cycles:
        print(f"\nCycle: {cycle.cycle_id}")
        print(f"Active Phase: {cycle.active_phase}")
        print()

        for phase_name in cycle.phases:
            phase = cycle.phases[phase_name]

            # Status indicator
            if phase.state == "Complete":
                indicator = "[x]"
            elif phase.state == "Active":
                indicator = "[>]"
            else:
                indicator = "[ ]"

            # Progress
            if phase.total_items > 0:
                progress = f"{phase.completed_items}/{phase.total_items}"
            else:
                progress = "-"

            print(f"  {indicator} {phase.name}: {progress}")

            # Show items in detailed mode
            if detailed and phase.items:
                for completed, text in phase.items:
                    check = "x" if completed else " "
                    print(f"      [{check}] {text}")


def validate_phase(cycle: CycleStatus) -> tuple[bool, list[str]]:
    """Validate current phase requirements are met."""
    phase = cycle.phases[cycle.active_phase]

    incomplete = []
    for completed, text in phase.items:
        if not completed:
            incomplete.append(text)

    can_advance = len(incomplete) == 0
    return can_advance, incomplete


def print_validation() -> None:
    """Validate and print phase requirements."""
    forge_dir = get_forge_dir()

    if not forge_dir.exists():
        print("FORGE not initialized.")
        return

    cycles = get_active_cycles()

    if not cycles:
        print("No active cycles.")
        return

    for cycle in cycles:
        print(f"Validating: {cycle.cycle_id}")
        print(f"Current Phase: {cycle.active_phase}")
        print()

        can_advance, incomplete = validate_phase(cycle)

        if can_advance:
            print("All requirements met. Ready to advance.")
            phase_list = list(cycle.phases.keys())
            if cycle.active_phase != phase_list[-1]:
                next_idx = phase_list.index(cycle.active_phase) + 1
                next_phase = phase_list[next_idx]
                print(f"Next phase: {next_phase}")
                print()
                print("Advance with: uv run forge_phase.py advance")
            else:
                print("Cycle complete. Archive with:")
                print(f"  uv run forge_cycle.py complete {cycle.cycle_id}")
        else:
            print("Incomplete items:")
            for item in incomplete:
                print(f"  - {item}")
            print()
            print("Complete these items before advancing.")


def phase_to_dict(phase: PhaseStatus) -> dict:
    """Serialize a PhaseStatus for JSON output."""
    return {
        "state": phase.state,
        "total_items": phase.total_items,
        "completed_items": phase.completed_items,
        "progress": phase.progress,
        "items": [
            {"completed": completed, "text": text}
            for completed, text in phase.items
        ],
    }


def status_data() -> dict:
    """Machine-readable status for --json."""
    if not get_forge_dir().exists():
        return {"initialized": False, "cycles": []}

    return {
        "initialized": True,
        "cycles": [
            {
                "cycle_id": cycle.cycle_id,
                "path": str(cycle.path),
                "active_phase": cycle.active_phase,
                "phases": {
                    name: phase_to_dict(phase)
                    for name, phase in cycle.phases.items()
                },
            }
            for cycle in get_active_cycles()
        ],
    }


def validation_data() -> dict:
    """Machine-readable validation for --validate --json."""
    if not get_forge_dir().exists():
        return {"initialized": False, "cycles": []}

    cycles = []
    for cycle in get_active_cycles():
        can_advance, incomplete = validate_phase(cycle)
        phase_list = list(cycle.phases.keys())
        next_phase = None
        if cycle.active_phase != phase_list[-1]:
            next_phase = phase_list[phase_list.index(cycle.active_phase) + 1]
        cycles.append(
            {
                "cycle_id": cycle.cycle_id,
                "active_phase": cycle.active_phase,
                "can_advance": can_advance,
                "incomplete": incomplete,
                "next_phase": next_phase,
            }
        )

    return {"initialized": True, "cycles": cycles}


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check FORGE status")
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed item status",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate phase requirements",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human-readable text",
    )

    args = parser.parse_args()

    if args.json:
        data = validation_data() if args.validate else status_data()
        print(json.dumps(data, indent=2))
    elif args.validate:
        print_validation()
    else:
        print_status(detailed=args.detailed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
