# Generate Phase ⚡

**Purpose**: Creation - AI writes code following TDD principles
**Lead Agents**: Developer, Tester, Reviewer

## Core Question

> "Does this code satisfy the acceptance criteria from Refine?"

## Key Principle: One Task Per Session

Each task should be completable in a single AI session. This prevents:
- Context pollution
- Mistake compounding
- Lost focus

Start fresh conversation for each new task.

## Goals

1. Write tests FIRST (RED phase)
2. Write minimal code to pass (GREEN phase)
3. Refactor while tests stay green (REFACTOR phase)
4. Preserve outputs immediately

## TDD Workflow: RED-GREEN-REFACTOR

### 1. RED: Write a Failing Test
```python
def test_user_login_success():
    # Arrange
    user = create_test_user("test@example.com", "password123")

    # Act
    result = login(email="test@example.com", password="password123")

    # Assert
    assert result.success is True
    assert result.token is not None
```

Run test → **Expect FAILURE** (feature doesn't exist yet)

### 2. GREEN: Write Minimal Code to Pass
```python
def login(email: str, password: str) -> LoginResult:
    user = find_user_by_email(email)
    if user and verify_password(password, user.password_hash):
        return LoginResult(success=True, token=generate_token(user))
    return LoginResult(success=False, token=None)
```

Run test → **Expect SUCCESS**

### 3. REFACTOR: Improve Without Breaking Tests
- Clean up code
- Remove duplication
- Improve naming
- Run tests → **Still passing**

## Tasks Checklist

- [ ] **Write failing tests first** (RED)
- [ ] **Implement minimal code** (GREEN)
- [ ] **Refactor while green** (REFACTOR)
- [ ] **Code review completed**
- [ ] **All tests passing**

## Structured Prompt Format

When generating code, use this structure:

```markdown
## Context
[What exists, where this fits, relevant constraints]

## Task
[Specific, single task to complete]

## Acceptance Criteria
[Given-When-Then from Refine phase]

## Format
[Expected output format, files, conventions]
```

## Agent Contributions

### Developer Agent (Primary)
Focus on:
- TDD discipline (tests FIRST)
- Clean code principles
- SOLID patterns
- Minimal implementation

### Tester Agent
Focus on:
- Test coverage
- Edge case testing
- Test quality review

### Reviewer Agent
Focus on:
- Code quality
- Best practices
- Security review
- Performance considerations

## Implementation Order

1. **Start with test file** - Write test before implementation
2. **Run test** - Verify it fails for the right reason
3. **Implement minimally** - Just enough to pass
4. **Run test** - Verify it passes
5. **Refactor** - Clean up while green
6. **Repeat** - Next test case

## Code Review Checklist

- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No obvious security issues
- [ ] No hardcoded secrets
- [ ] Error handling in place
- [ ] Edge cases covered

## When to Iterate vs Regenerate

**Iterate** when:
- Output is 80%+ correct
- Issues are minor tweaks
- Context is still relevant

**Regenerate fresh** when:
- Output has fundamental issues
- Approach is wrong
- Context is polluted

## Validation Gate

Before advancing to Evaluate, verify:

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

**Must have:**
- [ ] All acceptance criteria have corresponding tests
- [ ] Tests written and passing
- [ ] Code review completed
- [ ] All implementation tasks done

## Commands

```bash
# Mark test task complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "write tests"

# Mark implementation complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "implement"

# Mark review complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "code review"

# Validate and advance
uv run .claude/skills/forge/tools/forge_status.py --validate
uv run .claude/skills/forge/tools/forge_phase.py advance
```

## Common Mistakes

1. **Writing code before tests** - Always RED first
2. **Over-engineering** - Write minimal code to pass tests
3. **Skipping refactor** - Technical debt accumulates
4. **Skipping code review** - Fresh eyes catch bugs
5. **Ignoring failing tests** - Fix them, don't skip them
6. **Large sessions** - Keep to one task per session
7. **Not preserving outputs** - Save work immediately, don't rely on history
