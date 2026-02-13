# Generate Phase Guide

**Purpose**: Creation - AI writes code following TDD

## Key Process

**RED → GREEN → REFACTOR**

1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to make it pass
3. **REFACTOR**: Improve code while tests stay green

## Critical Rules

- One task per session (prevents context pollution)
- Tests MUST be written BEFORE implementation
- 80% minimum test coverage (90% for critical paths)
- No skipped tests

## Structured Prompts

When starting a task, provide:

1. **Context**: Relevant background, related code, dependencies
2. **Task**: Clear description of what to implement
3. **Criteria**: Acceptance criteria from Refine phase
4. **Format**: Expected output format, coding standards

## TDD Cycle

```
┌─────────────────────────────────────────┐
│  1. Write failing test (RED)            │
│     - Test describes expected behavior  │
│     - Run test, confirm it fails        │
├─────────────────────────────────────────┤
│  2. Write minimal code (GREEN)          │
│     - Just enough to pass the test      │
│     - No premature optimization         │
├─────────────────────────────────────────┤
│  3. Refactor (REFACTOR)                 │
│     - Improve code quality              │
│     - Tests must stay green             │
│     - Repeat cycle for next test        │
└─────────────────────────────────────────┘
```

## One Task Per Session

Why? Context pollution causes:
- AI mixing up requirements from different tasks
- Conflicting implementations
- Lost focus on acceptance criteria

Start fresh for each task with:
- Relevant context from earlier phases
- Clear task description
- Specific acceptance criteria

## Quality Gates

Before marking a task complete:
- [ ] All tests passing
- [ ] Coverage meets minimum threshold
- [ ] No linting errors
- [ ] Code follows project conventions

## Agent Teams Pattern

When using Claude Code Agent Teams for Generate:

**Team composition:**
- **Team Lead**: Developer (sonnet) — owns TDD implementation
- **Teammate**: Reviewer (sonnet) — validates code quality and criteria compliance

**Workflow:**
```
Orchestrate tasks
    ↓
┌─────────────────────────────────┐
│  For each task:                 │
│  1. Developer writes RED test   │
│  2. Developer writes GREEN code │
│  3. Developer REFACTORs         │
│  4. Reviewer checks criteria    │
│  5. Reviewer checks edge cases  │
└─────────────────────────────────┘
    ↓
All tasks complete → Evaluate
```

**What each teammate receives:**
- Developer: task description, acceptance criteria from Refine, interface specs, relevant context
- Reviewer: implementation output, acceptance criteria, edge case list from Refine

**When NOT to use teams:**
- Single-file bug fixes (just use a solo developer session)
- Trivial changes like config tweaks or copy updates
- Prototyping where speed matters more than review

## Completion Checklist

- [ ] Tests written before implementation
- [ ] All tests passing
- [ ] Coverage threshold met
- [ ] Code review completed
- [ ] Integration verified

## Commit Checkpoint

Commit after each completed TDD cycle, not just at the end of the phase:

- **After each RED-GREEN-REFACTOR cycle**: Commit the test and implementation together so every commit is a green build.
- **After code review**: Commit any review-driven changes as a separate commit.
- **After all tasks complete**: Commit `.forge/` state to record phase completion.

```
git add src/ tests/ .forge/
git commit -m "generate: implement <feature> with tests"
```

**Cadence**: Frequent small commits are better than one large commit at the end. Each commit should leave tests passing.

## Common Mistakes

- Writing code before tests
- Too many tasks in one session
- Skipping the refactor step
- Not running tests after changes

## Next Phase

When Generate is complete, advance to **Evaluate** where you verify output matches intent.
