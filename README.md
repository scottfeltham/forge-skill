# FORGE Skill for Claude Code

A standalone Claude Code skill that implements the FORGE development framework - Intent-Driven Development (IDD) for AI-assisted software engineering.

## What is FORGE?

FORGE (Focus-Orchestrate-Refine-Generate-Evaluate) is an Intent-Driven Development methodology that structures work into 5 sequential phases:

| Phase | Purpose | Key Question |
|-------|---------|--------------|
| **Focus** | Clarity | What are you actually building? |
| **Orchestrate** | Planning | How do you break this into pieces? |
| **Refine** | Precision | What specifically does "done" look like? |
| **Generate** | Creation | AI writes code following TDD |
| **Evaluate** | Verification | Does output match intent? |

**Core Principles**:
- Clarity before code
- Tests before implementation (TDD)
- One task per AI session
- AI is a tool, not the owner

## Installation

### Prerequisites

- Python 3.11+
- [Astral UV](https://docs.astral.sh/uv/) (for running single-file scripts)
- Claude Code CLI

### Global Setup (All Projects)

```bash
# Create skills directory and symlink
mkdir -p ~/.claude/skills
ln -s /path/to/forge-skill/.claude/skills/forge ~/.claude/skills/forge
```

### Per-Project Setup

```bash
# Copy to your project
cp -r forge-skill/.claude/skills/forge /path/to/your/project/.claude/skills/
```

## Quick Start

```bash
# Initialize FORGE in your project
uv run ~/.claude/skills/forge/tools/forge_init.py

# Start a new cycle
uv run ~/.claude/skills/forge/tools/forge_cycle.py new "feature-name"

# Check status
uv run ~/.claude/skills/forge/tools/forge_status.py

# Validate before advancing
uv run ~/.claude/skills/forge/tools/forge_status.py --validate

# Advance to next phase
uv run ~/.claude/skills/forge/tools/forge_phase.py advance
```

## The Five Phases

### 1. Focus - Clarity

Define what you're building and why.

**Required Outputs**:
- Problem statement and target users
- Testable success criteria
- System Context diagram (C4 L1)
- Clear scope boundaries

**Completion Test**: Can you explain what you're building to someone unfamiliar in under two minutes?

### 2. Orchestrate - Planning

Break the work into session-sized pieces.

**Required Outputs**:
- Container architecture (C4 L2)
- Component architecture (C4 L3)
- Dependency map
- Tasks sized for single AI sessions

**Completion Test**: Do you have a complete list of tasks in order, each small enough for one AI session?

### 3. Refine - Precision

Define exactly what "done" looks like. **No code in this phase.**

**Required Outputs**:
- Acceptance criteria in Given-When-Then format
- Interface specifications
- Edge cases by category
- Constraints vs criteria documented

**Completion Test**: Does every task have acceptance criteria specific enough to test?

### 4. Generate - Creation

AI writes code following strict TDD.

**Process**: RED → GREEN → REFACTOR
- Write failing test first
- Minimal code to pass
- Improve while tests stay green

**Rules**:
- One task per session
- 80% minimum coverage
- No skipped tests

### 5. Evaluate - Verification

Verify output matches intent.

**Process**:
- Line-by-line criteria check
- Edge case testing
- Security review
- Disposition decision: Accept / Revise / Reject

## CLI Tools

| Tool | Purpose |
|------|---------|
| `forge_init.py` | Initialize .forge/ in a project |
| `forge_cycle.py new` | Start a new development cycle |
| `forge_cycle.py list` | List all cycles |
| `forge_cycle.py complete` | Complete and archive a cycle |
| `forge_status.py` | Check current status |
| `forge_status.py --validate` | Validate phase requirements |
| `forge_phase.py advance` | Move to next phase |
| `forge_phase.py complete-task` | Mark a task complete |
| `forge_phase.py add-task` | Add a new task |
| `forge_learn.py add` | Capture a learning |
| `forge_learn.py list` | List all learnings |
| `forge_learn.py retro` | Run retrospective |

## Directory Structure

```
.claude/skills/forge/
├── skill.md                    # Main skill definition
├── tools/                      # Python CLI tools
│   ├── forge_init.py
│   ├── forge_cycle.py
│   ├── forge_phase.py
│   ├── forge_status.py
│   └── forge_learn.py
├── prompts/                    # Prompt templates
│   ├── prd-conversation.md
│   └── retrospective.md
└── cookbook/                   # Phase guides
    └── phases/
        ├── focus.md
        ├── orchestrate.md
        ├── refine.md
        ├── generate.md
        └── evaluate.md
```

## State Management

All FORGE state lives in `.forge/` directory:

```
.forge/
├── config.yaml           # Project configuration
├── context.md            # AI assistant context
├── learnings.md          # Knowledge base
└── cycles/
    ├── active/           # Current cycles
    └── completed/        # Archived cycles
```

## Phase Gates

Each phase has validation requirements:

**Focus → Orchestrate**
- Problem statement and users defined
- Success criteria are testable
- C4 L1 diagram exists
- Scope boundaries set

**Orchestrate → Refine**
- Architecture designed (C4 L2/L3)
- Dependencies mapped
- Tasks sized for sessions

**Refine → Generate**
- Given-When-Then criteria for all tasks
- Interfaces specified
- Edge cases enumerated
- NO CODE WRITTEN YET

**Generate → Evaluate**
- TDD followed (RED-GREEN-REFACTOR)
- Tests passing
- Coverage threshold met

**Evaluate → Complete**
- Criteria verified
- Edge cases tested
- Disposition decided

## License

MIT
