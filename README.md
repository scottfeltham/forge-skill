# FORGE Skill for Claude Code

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/scottfeltham/forge-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Claude Code skill that implements the FORGE development framework - Intent-Driven Development (IDD) for AI-assisted software engineering.

> ⭐ **This is the canonical FORGE implementation**, paired with forge-kit
> (a drop-in CLAUDE.md + phase-guard hook) for enforcement. For MCP-only
> tools (Cursor, VS Code, etc.) there is
> [forge-mcp-server](https://www.npmjs.com/package/forge-mcp-server),
> now in maintenance mode - it shares this skill's `.forge/` state format.

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

## Intent-Driven Development: the three pillars

FORGE is the cycle. **IDD is what the cycle carries.** Three pillars, and a work order missing one
is not a work order.

| Pillar | What it means | In a charter |
|---|---|---|
| **Intent** | Why this work exists — what is wrong now, and what changes | `intent:` |
| **Outcomes** | What must be observably true when it is done, **each naming the evidence that would falsify it** | `outcomes:` |
| **Responsibility** | The named human accountable for those outcomes. A person, not a role | `responsible:` |

An outcome that cannot be falsified is a hope, so outcomes carry their evidence with them:

> `channel` is a validated enum. A value outside `sms | email | whatsapp` is refused with a 422
> naming the parameter, **evidenced by a test that fails if the enum is widened to a bare string**.

### One work order, one responsibility

A charter is one unit of work, not a document that accretes. Two fields keep it that way:

| Field | Values | What it does |
|---|---|---|
| `scope:` | `epic` \| `feature` | Declares the size. A parent's scope restricts what its children may be |
| `parent:` | a sibling charter, or `scheme:ref` | Ties the work order to the collection it serves |

`parent:` takes a sibling's id, its filename, or a scheme — `basecamp:4821` names the commercial
record the work was sold under. Which system owns the collection is a property of the deployment,
not of the schema.

**Decomposition is checked, not trusted.** When an epic's Generate phase produces child charters,
the factory asserts that each child's scope is one its parent permits, that each names a parent,
that the parent it names is *this* one — and the expensive one, that **no parent outcome goes
uncited by a child**. A split that drops an outcome ships as a set of green cycles that never built
what was asked for.

What it deliberately does not check:

> Nothing here judges whether the split is **good**. That is the human's question at the approval
> gate, and the reason the gate is there.

Which is the responsibility pillar again: the machine can prove the decomposition is *complete*,
and only the named person can say it is *right*.

### Why pillars rather than only phases

Two 2026 publications describe agentic software development. Reading IDD against them shows what
the pillars buy, and where the field agrees they are missing.

| | **IDD** | **Anthropic, AI-native SDLC playbook** | **arXiv 2604.26275, *Agentic AI in the SDLC*** |
|---|---|---|---|
| **Intent** | `intent:` — the work order's reason to exist | `intent.md` — a direct match | Not a concept. Where intent comes from is outside the frame |
| **Outcomes** | First-class and evidence-bearing, declared **before** the work | A field *inside* `intent.md`. Falsification arrives later, as test strategy in `plan.md` and continuous evals | Measured across populations — SWE-bench 1.96% → 78.4% — never per unit of work |
| **Responsibility** | A named person, in the artefact | Approval **gates** — a role at a moment | Named as an urgent open problem: *"human–agent responsibility mapping"* |
| *Decomposition* | `scope:` and `parent:`, with parent outcomes checked against child coverage | `intent.md` is one canonical filename — a branch per intent, or a file that accretes | Task decomposition is an orchestration choice (L4), not a property of the work order |

**The paper's stated open problem is IDD's third pillar.** And outcomes is where IDD differs most
from the playbook: declaring the evidence before the work starts is what stops an acceptance test
drifting toward whatever was convenient to build.

**What the schema cannot do.** A `responsible:` field proves the name was filled in, not that the
person read the result. The pillar is enforced by the charter; it is honoured by a review small
enough to read — which is a practice, and lives outside this repo.

**Sources.** [The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) ·
[arXiv 2604.26275](https://arxiv.org/abs/2604.26275)

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
- Cycle review summary → `docs/<cycle>/cycle-review.md` (AC→test traceability, results, security, autonomy gate, reviewer checklist)
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
| `forge_status.py --json` | Machine-readable status (add `--validate` for validation JSON) |
| `forge_phase.py advance` | Move to next phase |
| `forge_phase.py complete-task` | Mark a task complete |
| `forge_phase.py add-task` | Add a new task |
| `forge_learn.py add` | Capture a learning |
| `forge_learn.py list` | List all learnings |
| `forge_learn.py retro` | Run retrospective |

## Directory Structure

```
.claude/skills/forge/
├── SKILL.md                    # Main skill definition
├── marketplace.json            # Marketplace metadata
├── tools/                      # Python CLI tools
│   ├── forge_init.py
│   ├── forge_cycle.py
│   ├── forge_phase.py
│   ├── forge_status.py
│   └── forge_learn.py
├── hooks/                      # Claude Code hooks
│   └── forge-phase-guard.sh    # Phase constraint enforcement
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

## Claude Code Integration

FORGE leverages Claude Code's native tools when available:

| Phase | Native Tool | Purpose |
|-------|-------------|---------|
| Focus | `AskUserQuestion` | Gather requirements, clarify scope |
| Orchestrate | `AskUserQuestion` | Validate architecture decisions |
| Refine | `AskUserQuestion` | Confirm acceptance criteria |
| Generate | `TodoWrite` | Track TDD implementation tasks |
| Evaluate | `AskUserQuestion` | Confirm verification results |

These per-phase confirmations are the **default**. A project can opt into
**autonomous (low-oversight) operation** — run all phases and the TDD loop without
pausing, gating a human in only at irreversible/production boundaries — by recording
a policy in its `.forge/context.md`. See "Autonomous (low-oversight) operation" in
`SKILL.md`. The required `cycle-review.md` deliverable is what keeps this safe: a
cycle can run unattended but cannot close without a sign-off artifact.

### Phase Enforcement Hook

To automatically enforce phase constraints (block code writes during Focus/Orchestrate/Refine):

1. **Copy hook to your project**:
   ```bash
   mkdir -p .claude/hooks
   cp ~/.claude/skills/forge/hooks/forge-phase-guard.sh .claude/hooks/
   chmod +x .claude/hooks/forge-phase-guard.sh
   ```

2. **Configure in `.claude/settings.json`**:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Edit|Write",
           "hooks": [
             {
               "type": "command",
               "command": ".claude/hooks/forge-phase-guard.sh"
             }
           ]
         }
       ]
     }
   }
   ```

3. **What the hook does**:
   - **Allows** writes to `docs/` in any phase (PRDs, specs, architecture)
   - **Allows** writes to `.forge/` (state management)
   - **Allows** test file writes in any phase (TDD support)
   - **Blocks** code writes during Focus, Orchestrate, Refine phases
   - **Allows** code writes during Generate and Evaluate phases

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
- Cycle review summary emitted (`docs/<cycle>/cycle-review.md`)
- Disposition decided

## Related Projects

- **[forge-mcp-server](https://github.com/scottfeltham/forge-mcp)** - MCP server for Cursor, VS Code, JetBrains, etc.
- **[Intent-Driven Development Book](https://github.com/scottfeltham/intentdrivendevelopment-book)** - The methodology behind FORGE

## Contributing

Contributions welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) first.

## License

MIT

## Author

Scott Feltham ([@scottfeltham](https://github.com/scottfeltham)) - scott@neoforge.co
