# Evaluate Phase ✅

**Purpose**: Verification - Does the output actually match intent?
**Lead Agents**: Tester, Reviewer, All Agents

## Core Question

> "Does this actually do what we specified in Refine?"

## Goals

1. Line-by-line verification against acceptance criteria
2. Test edge cases (listed AND unlisted)
3. Security review
4. Make disposition decision

## Disposition Framework

After verification, make one of these decisions:

| Disposition | When to Use |
|-------------|-------------|
| **Accept as-is** | Meets all criteria, no issues |
| **Accept with issues** | Meets criteria but has minor non-blocking issues |
| **Revise** | Partially meets criteria, specific fixes needed |
| **Reject** | Fundamentally wrong, regenerate from scratch |

## Tasks Checklist

- [ ] **Criteria verification** - Line-by-line check against Refine specs
- [ ] **Edge case testing** - Test listed AND unlisted cases
- [ ] **Security review** - Check for vulnerabilities
- [ ] **Make disposition** - Accept/Accept with issues/Revise/Reject
- [ ] **Conduct retrospective** - What worked? What didn't?
- [ ] **Document learnings** - Capture insights

## Criteria Verification Process

For each acceptance criterion from Refine:

```markdown
## Criterion: [Given-When-Then from Refine]

### Verification
- [ ] Actually tested (not just read the code)
- [ ] Passes as specified
- [ ] Edge cases checked

### Result
- ✅ Pass / ❌ Fail / ⚠️ Partial

### Notes
[Any observations, issues, or concerns]
```

## Edge Case Testing

Test both:
1. **Listed edge cases** - All cases enumerated in Refine
2. **Unlisted edge cases** - Think of cases you DIDN'T list

### Edge Case Categories Checklist
- [ ] Empty/null inputs
- [ ] Boundary values (min, max, first, last)
- [ ] Invalid data types and formats
- [ ] Timing and concurrency
- [ ] Failure scenarios
- [ ] Security cases (injection, bypass)

## Security Review Checklist

- [ ] No injection vulnerabilities (SQL, XSS, command)
- [ ] Authentication cannot be bypassed
- [ ] Authorization enforced properly
- [ ] Sensitive data not exposed in logs/errors
- [ ] No hardcoded secrets or credentials
- [ ] Rate limiting where appropriate

## Agent Contributions

### Tester Agent (Primary)
Focus on:
- Line-by-line criteria verification
- Actually run tests, don't just read code
- Test unlisted edge cases
- Report disposition recommendation

### Reviewer Agent
Focus on:
- Code quality assessment
- Security review
- Performance concerns
- Best practices compliance

### All Agents
Contribute to:
- Retrospective insights
- Learnings documentation
- Process improvements

## Retrospective Questions

**What went well?**
- Which practices were effective?
- What should we keep doing?

**What could improve?**
- Where did we struggle?
- What took longer than expected?

**Action items**
- What specific changes for next cycle?
- What learnings should be documented?

## Capturing Learnings

Add insights to the knowledge base:

```bash
# Successful pattern
uv run .claude/skills/forge/tools/forge_learn.py add success "TDD improved quality" "Writing tests first caught 3 bugs"

# Something to avoid
uv run .claude/skills/forge/tools/forge_learn.py add failure "Skipped specs" "Rushing past Refine led to rework"

# Reusable pattern
uv run .claude/skills/forge/tools/forge_learn.py add pattern "Repository pattern" "Clean separation improved testability"
```

## Validation Gate

Before completing cycle, verify:

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

**Must have:**
- [ ] All criteria verified (not just scanned)
- [ ] Disposition decision made
- [ ] At least one learning captured

**Strongly recommended:**
- [ ] Retrospective conducted
- [ ] Edge cases beyond the list tested

## Commands

```bash
# Run verification
uv run .claude/skills/forge/tools/forge_phase.py complete-task "criteria verification"

# Make disposition
uv run .claude/skills/forge/tools/forge_phase.py complete-task "disposition"

# Run retrospective
uv run .claude/skills/forge/tools/forge_learn.py retro

# Add learnings
uv run .claude/skills/forge/tools/forge_learn.py add <category> "title" "description"

# Complete cycle
uv run .claude/skills/forge/tools/forge_cycle.py complete <cycle-id>
```

## Common Mistakes

1. **Scanning instead of testing** - Actually run the tests, don't just read code
2. **Only testing listed cases** - Think of cases you didn't list
3. **Skipping security review** - Always check for vulnerabilities
4. **No disposition decision** - Be explicit about accept/revise/reject
5. **Skipping retrospective** - Miss valuable improvement opportunities
6. **Vague learnings** - Be specific with examples and context
