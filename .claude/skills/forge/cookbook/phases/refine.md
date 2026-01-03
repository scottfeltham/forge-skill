# Refine Phase ✏️

**Purpose**: Precision - Define exactly what "done" looks like BEFORE coding
**Lead Agents**: Tester, Architect, Reviewer

## Core Question

> "How will we know this is correct before we write any code?"

## ⚠️ CRITICAL: NO CODE IN THIS PHASE

This phase is about **specifications only**. The Generate phase is where code gets written.

## Goals

1. Write acceptance criteria in Given-When-Then format
2. Specify interfaces: inputs, outputs, error contracts
3. Enumerate edge cases by category
4. Define constraints (how to build) vs criteria (what to build)

## Acceptance Criteria Format

All criteria MUST follow Given-When-Then format:

```gherkin
Feature: User Authentication

Scenario: Valid user login
  Given a registered user with valid credentials
  When they submit their email and password
  Then they should receive a valid JWT token
  And be redirected to the dashboard

Scenario: Invalid password
  Given a registered user
  When they submit an incorrect password
  Then they should receive a 401 error
  And the error message should not reveal if the email exists
```

## Tasks Checklist

- [ ] **Acceptance criteria** - Given-When-Then for each feature
- [ ] **Interface specifications** - Inputs, outputs, error contracts
- [ ] **Edge case enumeration** - By category (see below)
- [ ] **Constraints defined** - Technical constraints and requirements
- [ ] **Review specifications** - Validate completeness

## Edge Case Categories

Systematically enumerate edge cases for each category:

| Category | Examples |
|----------|----------|
| **Empty/null inputs** | No data, empty strings, undefined |
| **Boundary values** | Min/max, first/last, zero/one |
| **Invalid data** | Wrong types, malformed, out of range |
| **Timing issues** | Out of order, concurrent, stale data |
| **Failure scenarios** | Network down, service unavailable |
| **Concurrent access** | Multiple users, race conditions |
| **Security cases** | Injection, bypass, unauthorized |

## Interface Specification Template

```markdown
## Interface: [Component/Function Name]

### Inputs
- `param1: Type` - Description, constraints
- `param2: Type` - Description, constraints

### Outputs
- **Success**: `ResponseType` - Description
- **Error**: `ErrorType` - Description

### Error Contracts
- `ValidationError` - When input fails validation
- `NotFoundError` - When resource doesn't exist
- `AuthError` - When unauthorized

### Constraints
- Must respond within 200ms
- Must be idempotent
- Must log all access attempts
```

## Agent Contributions

### Tester Agent (Primary)
Focus on:
- Acceptance criteria in Given-When-Then format
- Edge case enumeration by category
- Test scenario completeness
- **NO test implementation** - specifications only

### Architect Agent
Focus on:
- Interface specifications
- Input/output contracts
- Error handling requirements
- Technical constraints

### Reviewer Agent
Focus on:
- Specification completeness
- Criteria clarity
- Missing edge cases
- Ambiguity detection

## Validation Gate

Before advancing to Generate, verify:

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

**Must have:**
- [ ] Acceptance criteria for each task (Given-When-Then)
- [ ] Interface specifications complete
- [ ] Edge cases enumerated by category
- [ ] All specifications reviewed

## Commands

```bash
# Mark specification tasks complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "acceptance criteria"
uv run .claude/skills/forge/tools/forge_phase.py complete-task "interface specs"
uv run .claude/skills/forge/tools/forge_phase.py complete-task "edge cases"

# Validate and advance
uv run .claude/skills/forge/tools/forge_status.py --validate
uv run .claude/skills/forge/tools/forge_phase.py advance
```

## Common Mistakes

1. **Writing code** - This phase is specifications ONLY
2. **Vague criteria** - "Works correctly" is not testable
3. **Missing edge cases** - Use categories to be systematic
4. **Incomplete interfaces** - Every input, output, and error must be specified
5. **Skipping Given-When-Then** - All criteria must use this format
6. **Confusing constraints and criteria** - Constraints = HOW, Criteria = WHAT
