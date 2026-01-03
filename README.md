# FORGE Skill for Claude Code

A standalone Claude Code skill that implements the FORGE development framework - structured, phase-based development with no MCP server required.

## What is FORGE?

FORGE (Focus-Orchestrate-Refine-Generate-Evaluate) is an AI-first development methodology that structures work into 5 sequential phases:

| Phase | Purpose |
|-------|---------|
| 🎯 **Focus** | Requirements, test scenarios, architecture |
| 📝 **Orchestrate** | Task breakdown, dependencies, test strategy |
| 🔨 **Refine** | TDD implementation (RED-GREEN-REFACTOR) |
| 🚀 **Generate** | Build artifacts, deployment, documentation |
| 📊 **Evaluate** | Metrics, retrospective, learnings |

**Core Principle**: Test scenarios must be defined before any code is written.

## Installation

### Prerequisites

- Python 3.11+
- [Astral UV](https://docs.astral.sh/uv/) (for running single-file scripts)
- Claude Code CLI

### Setup

1. Clone or copy this skill to your Claude Code skills directory:

```bash
# Copy to your project
cp -r forge-skill/.claude/skills/forge /path/to/your/project/.claude/skills/

# Or symlink for shared use
ln -s /path/to/forge-skill/.claude/skills/forge ~/.claude/skills/forge
```

2. Initialize FORGE in your project:

```bash
cd /path/to/your/project
uv run .claude/skills/forge/tools/forge_init.py
```

This creates:
- `.forge/` directory with config and templates
- Updates `CLAUDE.md` with FORGE integration

## Usage

### Start a New Cycle

```bash
uv run .claude/skills/forge/tools/forge_cycle.py new "feature-name" --priority medium
```

### Check Status

```bash
uv run .claude/skills/forge/tools/forge_status.py
```

### Validate Before Advancing

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

### Advance to Next Phase

```bash
uv run .claude/skills/forge/tools/forge_phase.py advance
```

### Mark Tasks Complete

```bash
uv run .claude/skills/forge/tools/forge_phase.py complete-task "task description"
```

### Capture Learnings

```bash
uv run .claude/skills/forge/tools/forge_learn.py add pattern "title" "description"
```

### Run Retrospective

```bash
uv run .claude/skills/forge/tools/forge_learn.py retro
```

### Complete Cycle

```bash
uv run .claude/skills/forge/tools/forge_cycle.py complete <cycle-id>
```

## Directory Structure

```
.claude/skills/forge/
├── skill.md                    # Main skill definition
├── tools/                      # Python CLI tools
│   ├── forge_init.py          # Initialize .forge/
│   ├── forge_cycle.py         # Manage cycles
│   ├── forge_phase.py         # Manage phases
│   ├── forge_status.py        # Get status
│   └── forge_learn.py         # Manage learnings
├── prompts/                    # Prompt templates
│   ├── prd-conversation.md    # PRD building prompts
│   └── retrospective.md       # Retrospective prompts
└── cookbook/                   # Progressive disclosure docs
    ├── phases/                # Phase guides
    │   ├── focus.md
    │   ├── orchestrate.md
    │   ├── refine.md
    │   ├── generate.md
    │   └── evaluate.md
    ├── agents/                # Agent prompts
    │   ├── architect.md
    │   ├── developer.md
    │   ├── tester.md
    │   ├── devops.md
    │   ├── security.md
    │   ├── documentation.md
    │   └── reviewer.md
    └── workflows/             # Step-by-step guides
        ├── new-cycle.md
        ├── phase-advance.md
        └── complete-cycle.md
```

## Phase Gates

Each phase has validation requirements that must be met before advancing:

### Focus → Orchestrate
- ✅ Test scenarios defined (MANDATORY)
- ✅ Architecture designed
- ✅ Security risks identified

### Orchestrate → Refine
- ✅ Minimum 3 tasks defined
- ✅ Dependencies mapped
- ✅ Test strategy documented

### Refine → Generate
- ✅ Tests written and passing
- ✅ Code review completed
- ✅ Implementation tasks done

### Generate → Evaluate
- ✅ Build artifacts created
- ✅ Documentation updated

### Evaluate → Complete
- ✅ Success metrics collected
- ✅ Retrospective conducted (recommended)

## How It Works

1. **Skill Activation**: Claude detects FORGE-related requests ("forge", "new cycle", "advance phase", etc.)

2. **Auto-Context**: Skill checks `.forge/` status before any action

3. **Progressive Disclosure**: Routes to relevant cookbook docs based on current phase and request

4. **Phase Enforcement**: Blocks inappropriate work (e.g., coding in Focus phase)

5. **Validation Gates**: Requires completion of mandatory tasks before phase advancement

## Differences from FORGE MCP

This skill **replaces** the FORGE MCP server:

| Feature | MCP Version | Skill Version |
|---------|-------------|---------------|
| Server required | Yes | No |
| State management | MCP server | Python CLI tools |
| Integration | MCP protocol | Direct file access |
| Portability | Needs MCP setup | Works anywhere |

## License

MIT
