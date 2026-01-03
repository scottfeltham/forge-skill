# Complete Cycle Workflow

Archive a finished development cycle.

## Prerequisites

- Cycle in Evaluate phase
- Success metrics collected
- Retrospective conducted (recommended)

## Steps

### 1. Verify Cycle Status

```bash
uv run .claude/skills/forge/tools/forge_status.py
```

Ensure:
- Phase: Evaluate
- Critical tasks completed
- Ready for completion

### 2. Run Retrospective

If not already done:
```bash
uv run .claude/skills/forge/tools/forge_learn.py retro
```

Guide through:
- What went well?
- What could improve?
- Action items for next cycle

### 3. Capture Learnings

Add insights to knowledge base:
```bash
# Successful practices
uv run .claude/skills/forge/tools/forge_learn.py add success "title" "description"

# Things to avoid
uv run .claude/skills/forge/tools/forge_learn.py add failure "title" "description"

# Reusable patterns
uv run .claude/skills/forge/tools/forge_learn.py add pattern "title" "description"
```

### 4. Validate Completion

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

Check for:
- [ ] Success metrics task completed
- [ ] Retrospective conducted (recommended)

### 5. Complete the Cycle

```bash
uv run .claude/skills/forge/tools/forge_cycle.py complete <cycle-id> --notes "Completion notes"
```

This will:
- Move cycle from `active/` to `completed/`
- Add completion timestamp
- Archive with notes

### 6. Verify Completion

```bash
uv run .claude/skills/forge/tools/forge_cycle.py list --all
```

Should show cycle in completed list.

## Example Session

```
User: "Let's wrap up this cycle"

Agent Actions:
1. Run: uv run tools/forge_status.py
2. Confirm in Evaluate phase
3. Ask: "Before completing, let's do a quick retrospective.
   What went well in this cycle?"
4. Capture learnings
5. Run: uv run tools/forge_cycle.py complete <id>
6. Announce completion
7. Ask: "Ready to start a new cycle, or would you like to
   review the learnings we captured?"
```

## Retrospective Questions

### What Went Well?
- Which practices were effective?
- What tools helped?
- What would you do again?

### What Could Improve?
- Where did you struggle?
- What took longer than expected?
- What would you do differently?

### Action Items
- What specific changes for next time?
- What should be documented?
- What processes need adjustment?

## Learning Categories

| Category | Use For |
|----------|---------|
| `success` | Practices that worked well |
| `failure` | Things to avoid |
| `pattern` | Reusable solutions |
| `antipattern` | Solutions to avoid |
| `tool` | Tool recommendations |
| `process` | Process improvements |

## Force Completion (Not Recommended)

If Evaluate tasks aren't complete:
```bash
uv run .claude/skills/forge/tools/forge_cycle.py complete <cycle-id> --force
```

⚠️ **Warning**: Skipping evaluation means:
- Missing insights for improvement
- Repeating mistakes
- Lost learnings

## After Completion

### Review Learnings
```bash
uv run .claude/skills/forge/tools/forge_learn.py list
```

### Start Next Cycle
```bash
uv run .claude/skills/forge/tools/forge_cycle.py new "next-feature"
```

### View History
```bash
uv run .claude/skills/forge/tools/forge_cycle.py list --all
```

## Tips

1. **Don't skip retrospective** - Most valuable part of the cycle
2. **Be specific in learnings** - Include context and examples
3. **Add completion notes** - Future you will appreciate the context
4. **Celebrate completion** - Finishing a cycle is an accomplishment
5. **Rest before next cycle** - Avoid burnout, take a breath
