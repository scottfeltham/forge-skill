---
name: forge
description: |
  FORGE development framework for Intent-Driven Development (IDD).
  Use for: forge, FORGE, new cycle, start cycle, advance phase, next phase,
  checkpoint, validate phase, focus, orchestrate, refine, generate, evaluate,
  cycle status, complete cycle, add learning, retrospective, TDD workflow,
  product plan, mvp, roadmap, architecture, PRD, hil, hil mode,
  human in the loop, iterate, tweak, refine cycle.
allowed-tools: Read, Write, Edit, Bash(uv:*), Bash(python:*), Glob, Grep
---

# FORGE Development Framework

FORGE (Focus-Orchestrate-Refine-Generate-Evaluate) is an Intent-Driven Development (IDD) methodology for AI-assisted software development.

## Interactive Workflow: Clarity Before Action

During **Focus, Orchestrate, and Refine** phases, you must gain clarity before proceeding:

1. **Assess clarity** - Are the requirements/inputs clear or vague?
2. **If vague** → Ask targeted clarifying questions (use `prompts/prd-conversation.md` as a guide)
3. **Always** → Summarize your understanding and confirm with the user before advancing

### Phase Confirmation Pattern

| Phase | Summarize & Confirm |
|-------|---------------------|
| **Focus** | "Problem: X. Users: Y. Success: Z. Boundaries: [in/out of scope]. Correct?" |
| **Orchestrate** | "Architecture: N containers/components. Dependencies: [map]. Task breakdown: [list]. Correct?" |
| **Refine** | "Acceptance criteria: [Given-When-Then]. Edge cases: [categories]. Interfaces: [specs]. Correct?" |

Only advance after user confirms. Generate and Evaluate phases may proceed without additional confirmation once Refine is validated.

## Native Tool Integration (Claude Code)

When running in Claude Code, leverage native tools for enhanced workflow:

| Phase | Native Tool | Purpose |
|-------|-------------|---------|
| **Focus** | `AskUserQuestion` | Gather requirements, clarify scope, confirm problem statement |
| **Orchestrate** | `AskUserQuestion` | Validate architecture decisions, confirm task breakdown |
| **Refine** | `AskUserQuestion` | Confirm acceptance criteria, validate edge cases |
| **Generate** | `TodoWrite` | Track implementation tasks (RED-GREEN-REFACTOR steps) |
| **Evaluate** | `AskUserQuestion` | Confirm verification results, get disposition decision |

**Adaptive behavior:**
- If `AskUserQuestion` is available, use it for structured clarification with options
- If `TodoWrite` is available, use it to track Generate phase tasks
- Fall back to conversational clarification in non-Claude-Code environments

**Example - Using AskUserQuestion in Focus:**
```
When clarifying requirements, present structured options:
- "What is your target user base?" with options like "Internal team", "External customers", "API consumers"
- This provides better UX than open-ended questions
```

**Example - Using TodoWrite in Generate:**
```
Track TDD workflow:
1. [in_progress] Write failing test for feature X
2. [pending] Implement minimal code to pass
3. [pending] Refactor while tests stay green
```

### Resolving Clarity Issues (Any Phase)

If clarity issues arise at any phase, you may:
- Ask targeted clarifying questions
- Invoke specialist agents for guidance
- Recommend returning to an earlier phase

## Autonomous (low-oversight) operation

By default the Focus/Orchestrate/Refine phases pause to "Summarize & Confirm" with
the user. A project can opt into **autonomous operation** instead — run all phases
and the Generate TDD loop without pausing, and surface to a human **only** at a
defined risk boundary. Enable it by recording an operating policy in the project's
`.forge/context.md`; the policy governs every cycle in that project.

A sound policy has two halves:

- **Always autonomous** — planning + all phase docs, writing tests, RED→GREEN→REFACTOR,
  dark/unwired code, behaviour-preserving refactors, reversible commits to trunk,
  staging deploys, phase advancement and internal validation. Decide and report;
  don't ask.
- **STOP and get a human (the only gates)** — actions that are irreversible or touch
  production reality. Define these concretely for the project; typical examples:
  executing credential/IAM changes, enabling auth lockdown on a live endpoint,
  schema migration / bulk writes on a production datastore, anything that sends real
  messages or moves real money, deleting a code path still serving live traffic, and
  production deploys. Also stop if a Focus requirement is genuinely ambiguous and
  can't be resolved from the project's own docs/code.

The `cycle-review.md` deliverable (see Evaluate, below) is what makes this safe: a
cycle can *run* without a human in the loop, but it can't *close* without leaving a
review artifact the human signs off on, and it halts at the first gated step.

> **Naming caveat:** despite the name, **HIL mode is the *leaner* cycle, not the
> *more-supervised* one.** It skips Focus/Orchestrate (planning) — it does not add
> human gates. Autonomy is the policy above; HIL vs Full is only about how many
> phases run. The two compose: prefer HIL for well-briefed work and run it autonomously.

## HIL Mode (Human-in-the-Loop)

HIL mode is a streamlined 3-phase cycle for active development — when you're already in the code, know what you're building, and are iterating on existing capabilities.

### When to Use HIL vs Full FORGE

| Signal | Mode | Reasoning |
|--------|------|-----------|
| Entirely new feature or capability | **Full** | Needs Focus (what/why) and Orchestrate (architecture) |
| Refining/tweaking existing design | **HIL** | Context already established, jump to Refine |
| Bug fix with clear reproduction | **HIL** | Acceptance criteria are the fix; skip planning |
| Design iteration after feedback | **HIL** | Re-enter at Refine with updated criteria |
| New system or major component | **Full** | Needs architectural decisions upfront |
| Updating processes to fit a design | **HIL** | The "what" is known; define "done" and implement |

### HIL Workflow

```
Refine → Generate → Evaluate (→ loop back to Refine if needed)
```

1. **Refine**: Define what "done" looks like for this specific change
   - Acceptance criteria (Given-When-Then)
   - Interface changes (if any)
   - Edge cases for the change
2. **Generate**: Implement via TDD (RED → GREEN → REFACTOR)
3. **Evaluate**: Verify against criteria, decide disposition

### Creating a HIL Cycle

```bash
uv run "$FORGE_TOOLS/forge_cycle.py" new "description of change" --mode hil
```

### Iterative HIL Pattern

For ongoing active development, each update/tweak can be its own HIL cycle:
1. Create HIL cycle describing the change
2. Refine: Specify acceptance criteria for this iteration
3. Generate: Implement with TDD
4. Evaluate: Verify and decide — Accept, or loop back to Refine

This keeps FORGE discipline (specifications before code, TDD, verification) without the overhead of full planning phases when the context is already established.

## Tool Commands

The tool scripts are in the `tools/` subdirectory of this skill. Before running the first command, resolve the skill's install location:

```bash
# Local project install takes priority over global
if [ -d ".claude/skills/forge/tools" ]; then
  FORGE_TOOLS=".claude/skills/forge/tools"
else
  FORGE_TOOLS="$HOME/.claude/skills/forge/tools"
fi
```

Use the resolved path for all commands below. Since shell state does not persist between commands, prefix each invocation: `FORGE_TOOLS=<resolved-path> && uv run "$FORGE_TOOLS/forge_init.py"`, or simply substitute the resolved path directly.

| User Request | Command |
|-------------|---------|
| Initialize FORGE | `uv run "$FORGE_TOOLS/forge_init.py"` |
| Start new cycle | `uv run "$FORGE_TOOLS/forge_cycle.py" new "name"` |
| Start HIL cycle | `uv run "$FORGE_TOOLS/forge_cycle.py" new "name" --mode hil` |
| Check status | `uv run "$FORGE_TOOLS/forge_status.py"` |
| Validate phase | `uv run "$FORGE_TOOLS/forge_status.py" --validate` |
| Advance phase | `uv run "$FORGE_TOOLS/forge_phase.py" advance` |
| Complete task | `uv run "$FORGE_TOOLS/forge_phase.py" complete-task "desc"` |
| Add task | `uv run "$FORGE_TOOLS/forge_phase.py" add-task "desc"` |
| Complete cycle | `uv run "$FORGE_TOOLS/forge_cycle.py" complete <id>` |
| Add learning | `uv run "$FORGE_TOOLS/forge_learn.py" add <cat> "title" "desc"` |
| Retrospective | `uv run "$FORGE_TOOLS/forge_learn.py" retro` |

Learning categories: `pattern`, `anti-pattern`, `decision`, `tool`

## Core Concepts

### Intent-Driven Development Triad

- **Intent** - Why the work exists; the problem being solved
- **Outcomes** - Observable, defensible changes in reality
- **Accountability** - Single owner responsible for consequences

### The Five Phases

| Phase | Purpose | Key Question |
|-------|---------|--------------|
| **FOCUS** | Clarity | What are you actually building? |
| **ORCHESTRATE** | Planning | How do you break this into pieces? |
| **REFINE** | Precision | What specifically does "done" look like? |
| **GENERATE** | Creation | AI produces deliverables matching scope |
| **EVALUATE** | Verification | Does output match intent? |

### Product-Level Cycles

FORGE cycles work at **any scope** - feature, epic, or entire product/MVP. The phases are identical; the **Generated output** changes based on scope.

| Phase | Feature-Level | Product-Level |
|-------|--------------|---------------|
| **Focus** | What feature & why | What product/MVP & why |
| **Orchestrate** | Component architecture, task breakdown | System architecture, feature breakdown |
| **Refine** | Feature acceptance criteria, interfaces | Product success criteria, per-feature scope |
| **Generate** | Code (TDD) | Documentation: PRD, architecture docs, roadmap, feature cycle plan |
| **Evaluate** | Verify code matches intent | Verify plans match intent |

At the product level, Generate produces documentation and plans - not code. Each planned feature then becomes its own FORGE cycle.

**Product-level workflow:**
1. `forge_cycle.py new "mvp-product-name"` - Create a product-level cycle
2. Work through Focus/Orchestrate/Refine at the product level
3. Generate: Produce PRD, architecture docs, and ordered list of feature cycles
4. Evaluate: Verify plans are complete and match intent
5. Each feature becomes its own FORGE cycle with code as output

## Phase Details

### 1. FOCUS - Clarity

**Required Outputs**:
- Problem statement and target users defined
- Testable success criteria (not vague aspirations)
- System Context diagram (C4 Level 1)
- Clear boundaries on what you WON'T build

### 2. ORCHESTRATE - Planning

**Required Outputs**:
- Container architecture (C4 Level 2)
- Component architecture (C4 Level 3)
- Dependency map
- Tasks sized for single AI sessions

### 3. REFINE - Precision

**CRITICAL**: No code in this phase - specifications only.

**Required Outputs**:
- Acceptance criteria in Given-When-Then format
- Interface specifications (inputs, outputs, errors)
- Edge cases by category (empty/null, boundary, invalid, timing, failure, concurrent)
- Constraints vs criteria documented

### 4. GENERATE - Creation

**Process**: RED → GREEN → REFACTOR
1. Write failing test first
2. Minimal code to pass
3. Improve while tests stay green

**Rules**:
- One task per session
- Tests BEFORE implementation
- 80% minimum coverage

### 5. EVALUATE - Verification

**Process**:
- Line-by-line check against acceptance criteria
- Test edge cases (specified AND discovered)
- Security review
- Integration testing

**Dispositions**: Accept | Accept with issues | Revise | Reject

## Document Creation

During each phase, create and maintain documents in `docs/`. Documents are organized per cycle/feature:

```
docs/
├── prd/
│   └── <cycle-name>.md         # Focus: Problem statement, users, success criteria, scope
├── tasks/
│   └── <cycle-name>.md         # Orchestrate: Session-sized task breakdown
└── <cycle-name>/
    ├── system-context.md       # Focus: C4 Level 1 - system boundaries
    ├── containers.md           # Orchestrate: C4 Level 2 - deployable units
    ├── components.md           # Orchestrate: C4 Level 3 - internal structure
    ├── acceptance-criteria.md  # Refine: Given-When-Then scenarios
    ├── interfaces.md           # Refine: inputs, outputs, error contracts
    ├── edge-cases.md           # Refine: categorized edge cases
    └── cycle-review.md         # Evaluate: review-ready summary for human sign-off
```

**Phase → Document mapping:**
| Phase | Create/Update |
|-------|---------------|
| Focus | `prd/<cycle>.md`, `<cycle>/system-context.md` |
| Orchestrate | `tasks/<cycle>.md`, `<cycle>/containers.md`, `<cycle>/components.md` |
| Refine | `<cycle>/acceptance-criteria.md`, `<cycle>/interfaces.md`, `<cycle>/edge-cases.md` |
| Evaluate | `<cycle>/cycle-review.md` (AC→test traceability, results, security, autonomy gate, reviewer checklist — see `cookbook/phases/evaluate.md`) |

Create documents as you complete phase work. These are the source of truth for Generate and Evaluate phases.

## State Management

All cycle state lives in `.forge/`:
```
.forge/
├── config.yaml
├── context.md
├── learnings.md
└── cycles/
    ├── active/
    └── completed/
```

## Phase Blocking

- Cannot write code during Focus, Orchestrate, or Refine
- Cannot advance without completing mandatory items
- Evaluation may send you back to earlier phases

## Commit Cadence

Commit after every meaningful checkpoint — not just at the end of a phase:

- **After each phase checklist item**: When you complete a deliverable (e.g., PRD, acceptance criteria, test suite), commit it immediately.
- **After phase advancement**: Commit `.forge/` state whenever a phase advances so cycle progress is never lost.
- **During Generate**: Commit after each completed TDD cycle (RED-GREEN-REFACTOR), not just at task completion.
- **Commit message convention**: Prefix with the phase name, e.g., `focus: add PRD and system context diagram` or `generate: implement user auth with tests`.

### Hook-Based Enforcement (Claude Code)

For automated phase constraint enforcement, configure hooks in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": [".claude/hooks/forge-phase-guard.sh"]
      }
    ]
  }
}
```

The hook script:
- Reads current phase from `.forge/cycles/active/`
- **Allows** all writes to `docs/` (specs, PRDs, architecture docs)
- **Blocks** code writes during Focus, Orchestrate, Refine phases
- **Allows** code writes during Generate and Evaluate phases

Install the hook:
```bash
mkdir -p .claude/hooks
cp path/to/forge-skill/.claude/hooks/forge-phase-guard.sh .claude/hooks/
chmod +x .claude/hooks/forge-phase-guard.sh
```

## Model Routing

When using Claude Code Agent Teams, assign model tiers based on cognitive demand:

| Agent | Model | Reasoning |
|-------|-------|-----------|
| Architect | opus | Architecture decisions, trade-off analysis |
| Security | opus | Threat modeling, adversarial thinking |
| Developer | sonnet | Well-specified implementation tasks |
| Tester | sonnet | Test writing from specifications |
| DevOps | sonnet | Infrastructure, config patterns |
| Documentation | haiku | Structured writing from existing content |
| Integration Coordinator | sonnet | Cross-component coordination |
| Reviewer | sonnet | Code quality checks against criteria |

**Complexity overrides:**
- Promote to opus when the task involves novel architecture, ambiguous requirements, or security-critical decisions
- Demote to haiku for boilerplate generation, formatting, or simple lookups
- Default tier applies when task complexity matches the agent's typical workload

## Agent Teams

Map FORGE phases to Claude Code Agent Teams compositions:

| Phase | Team Lead | Teammates | Pattern |
|-------|-----------|-----------|---------|
| Focus | Architect (opus) | Security (opus), Documentation (haiku) | Lead defines scope; teammates assess risks and draft PRD |
| Orchestrate | Architect (opus) | — | Solo decomposition and dependency analysis |
| Refine | Architect (opus) | Tester (sonnet) | Lead defines interfaces; teammate writes acceptance criteria |
| Generate | Developer (sonnet) | Reviewer (sonnet) | Lead implements via TDD; reviewer checks each task against criteria |
| Evaluate | Tester (sonnet) | Reviewer (sonnet), Security (opus) | Tester verifies criteria; reviewer does final code review; security does adversarial review |

**Generate phase detail:**
- Each task from Orchestrate becomes one teammate session
- Developer receives: task description, acceptance criteria from Refine, interface specs
- Reviewer checks after each TDD cycle: test-first compliance, criteria alignment, code quality
- One task per session prevents context pollution

**Evaluate phase detail:**
- Reviewer performs final holistic review: security posture, integration contracts, overall quality
- Tester verifies acceptance criteria line-by-line and edge case coverage
- Security agent performs adversarial review on security-critical code
- Reviewer disposition feeds into cycle disposition decision

## Key Principle

**Clarity before code** - Time in Focus, Orchestrate, and Refine prevents waste in Generate and Evaluate.
