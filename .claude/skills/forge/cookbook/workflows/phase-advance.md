# Phase Advance Workflow

Move from current phase to the next phase.

## Prerequisites

- Active cycle exists
- Current phase requirements met

## Steps

### 1. Check Current Status

```bash
uv run .claude/skills/forge/tools/forge_status.py
```

Note:
- Current phase
- Task completion
- Overall progress

### 2. Validate Readiness

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

This checks phase-specific requirements:

| From | To | Requirements |
|------|-----|--------------|
| Focus | Orchestrate | Test scenarios, architecture, security |
| Orchestrate | Refine | 3+ tasks, dependencies, test strategy |
| Refine | Generate | Tests passing, code review, tasks done |
| Generate | Evaluate | Build artifacts, documentation |
| Evaluate | Complete | Success metrics |

### 3. Address Blocking Issues

If validation fails, you'll see blocking issues:

```
❌ Blocking Issues:
   • MANDATORY: Test scenarios must be defined
   • Architecture task not completed
```

Complete required tasks:
```bash
uv run .claude/skills/forge/tools/forge_phase.py complete-task "test scenarios"
uv run .claude/skills/forge/tools/forge_phase.py complete-task "architecture"
```

### 4. Advance Phase

Once validated:
```bash
uv run .claude/skills/forge/tools/forge_phase.py advance
```

### 5. Read Next Phase Guide

After advancing, read the new phase's cookbook:
- `cookbook/phases/focus.md`
- `cookbook/phases/orchestrate.md`
- `cookbook/phases/refine.md`
- `cookbook/phases/generate.md`
- `cookbook/phases/evaluate.md`

## Example Session

```
User: "I think we're ready to move to the next phase"

Agent Actions:
1. Run: uv run tools/forge_status.py --validate
2. Check output for issues
3. If issues exist:
   - List what needs to be done
   - Help complete remaining tasks
4. If no issues:
   - Run: uv run tools/forge_phase.py advance
   - Announce new phase
   - Read new phase cookbook
   - Guide user on next steps
```

## Force Advance (Not Recommended)

If you must bypass validation:

```bash
uv run .claude/skills/forge/tools/forge_phase.py advance --force
```

⚠️ **Warning**: Skipping validation often leads to:
- Missing requirements causing rework
- Bugs from skipped tests
- Technical debt accumulation

## Phase Transition Summary

### Focus → Orchestrate
You're moving from "what" to "how":
- Requirements → Task breakdown
- Test scenarios → Test strategy
- Architecture → Detailed design

### Orchestrate → Refine
You're moving from planning to doing:
- Task list → TDD implementation
- Test strategy → Actual tests
- Design → Code

### Refine → Generate
You're moving from building to shipping:
- Code → Build artifacts
- Tests → Final validation
- Implementation → Documentation

### Generate → Evaluate
You're moving from shipping to learning:
- Deployment → Metrics collection
- Documentation → Retrospective
- Release → Learnings capture

## Tips

1. **Don't rush validation** - Each gate exists for a reason
2. **Complete don't skip** - Missing work will haunt you later
3. **Celebrate progress** - Moving phases is an achievement
4. **Prepare for next phase** - Read the cookbook before diving in
