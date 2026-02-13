# Evaluate Phase Guide

**Purpose**: Verification - Does output match intent?

## Key Question

Does the implementation satisfy all acceptance criteria from Refine, handle edge cases correctly, and meet security requirements?

## Verification Process

1. **Criteria Check**: Line-by-line against Refine specs
2. **Edge Case Testing**: Both specified AND discovered
3. **Integration Testing**: Components work together
4. **Security Review**: OWASP top 10, auth, data exposure

## Criteria Verification

For each acceptance criterion from Refine:
- [ ] Test exists that verifies the criterion
- [ ] Test passes consistently
- [ ] Behavior matches specification exactly

## Edge Case Testing

Test the edge cases enumerated in Refine:
- Empty/null inputs
- Boundary values
- Invalid inputs
- Timing issues
- Failure scenarios
- Concurrent access

Also test edge cases discovered during Generate.

## Security Review Checklist

- [ ] Input validation (server-side)
- [ ] Parameterized queries (no SQL injection)
- [ ] Authentication on protected endpoints
- [ ] Authorization checks for resources
- [ ] Sensitive data encrypted
- [ ] No secrets in code or logs

## Integration Testing

- [ ] Components communicate correctly
- [ ] Data flows as designed
- [ ] Error handling works across boundaries
- [ ] Performance meets requirements

## Agent Teams Pattern

When using Claude Code Agent Teams for Evaluate:

**Team composition:**
- **Team Lead**: Tester (sonnet) — verifies acceptance criteria and edge cases
- **Teammate**: Security (opus) — performs adversarial review and threat analysis

**Verification workflow:**
```
Generate output
    ↓
┌──────────────────────────────────────┐
│  Tester (lead):                      │
│  1. Line-by-line criteria check      │
│  2. Run edge case tests              │
│  3. Verify integration points        │
├──────────────────────────────────────┤
│  Security (teammate):                │
│  1. OWASP top 10 review             │
│  2. Auth/authz bypass attempts       │
│  3. Data exposure analysis           │
└──────────────────────────────────────┘
    ↓
Disposition decision
```

**Competing hypotheses pattern for debugging:**
When a test fails or unexpected behavior is found, use Security (opus) to generate adversarial hypotheses about root cause while Tester (sonnet) investigates the most likely explanation. This parallel approach catches subtle issues that sequential investigation misses.

## Disposition Decisions

| Decision | Meaning | Action |
|----------|---------|--------|
| **Accept** | Meets all criteria | Ship/integrate |
| **Accept with issues** | Works but has minor issues | Document, plan fixes |
| **Revise** | Doesn't meet criteria | Back to Generate |
| **Reject** | Fundamental problems | Back to Orchestrate/Focus |

## When to Revise vs Reject

**Revise** (back to Generate):
- Implementation bug
- Missing edge case handling
- Performance issue fixable in code

**Reject** (back to earlier phase):
- Requirements were wrong
- Architecture doesn't support the feature
- Scope needs to change

## Completion Checklist

- [ ] All criteria verified
- [ ] Edge cases tested
- [ ] Integration tested
- [ ] Security reviewed
- [ ] Disposition decided

## After Evaluate

If **Accept**: Complete the cycle
```bash
uv run forge_cycle.py complete <cycle-id>
```

If **Revise**: Return to Generate with specific feedback

If **Reject**: Return to appropriate earlier phase

Consider running a retrospective:
```bash
uv run forge_learn.py retro
```

## Commit Checkpoint

Commit verification results and disposition decisions:

- **Verification results**: Commit any additional tests or fixes discovered during evaluation.
- **Disposition decision**: Commit `.forge/` state recording the Accept/Revise/Reject decision.
- **Retrospective** (if run): Commit the retrospective output in `.forge/retrospectives/`.

```
git add .forge/ tests/
git commit -m "evaluate: verify <cycle> — <disposition>"
```

If the disposition is **Revise**, commit what you have before returning to Generate so progress is preserved.

## Common Mistakes

- "Looks right" instead of systematic verification
- Skipping edge cases that seem unlikely
- Missing security review
- Not documenting issues found
