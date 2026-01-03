# PRD Conversation Prompts

Use these prompts to guide users through requirements gathering.

## Initial Feature Discussion

When user starts a new cycle with minimal information, ask:

### Understanding the Problem

```
Before we design the solution, let's understand the problem:

1. **Who** is this for? (user type, role, persona)
2. **What** problem does it solve for them?
3. **Why** is this important now?
4. **How** do they currently handle this? (if at all)
```

### Defining Success

```
Let's define what success looks like:

1. **Test Scenarios**: How will we verify this works?
   - Happy path: What's the main success scenario?
   - Edge cases: What unusual situations should we handle?
   - Error cases: What should happen when things go wrong?

2. **Acceptance Criteria**: What must be true for this to be "done"?
   - [ ] Criterion 1
   - [ ] Criterion 2
   - [ ] Criterion 3
```

### Technical Context

```
Let's understand the technical context:

1. **Integrations**: What systems does this touch?
2. **Data**: What data is needed? Created? Modified?
3. **Performance**: Any speed/scale requirements?
4. **Security**: Any sensitive data or access concerns?
```

### Scope Definition

```
Let's be clear about scope:

**In Scope** (what we WILL do):
-

**Out of Scope** (what we WON'T do this cycle):
-

**Dependencies** (what we need from others):
-
```

## Test Scenario Template

```gherkin
Feature: [Feature Name]

  Background:
    Given [common setup for all scenarios]

  Scenario: [Happy Path - Main Success]
    Given [initial context]
    When [user action]
    Then [expected outcome]
    And [additional verification]

  Scenario: [Edge Case 1]
    Given [edge case context]
    When [user action]
    Then [expected handling]

  Scenario: [Error Case - Invalid Input]
    Given [error context]
    When [user provides invalid input]
    Then [error is handled gracefully]
    And [user sees helpful message]
```

## PRD Summary Template

After gathering information, summarize:

```markdown
# PRD: [Feature Name]

## Problem
[1-2 sentence problem statement]

## Solution
[1-2 sentence solution summary]

## User Stories
- As a [user], I want to [action] so that [benefit]

## Test Scenarios
[Link to or include test scenarios]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Technical Notes
- [Key technical decisions]
- [Integration points]
- [Constraints]

## Out of Scope
- [What we're explicitly NOT doing]

## Success Metrics
- [How we'll measure success]
```

## Conversation Flow

```
1. START: "What feature are you building?"
   ↓
2. PROBLEM: "What problem does this solve?"
   ↓
3. USERS: "Who will use this?"
   ↓
4. SUCCESS: "How will we know it works?" (TEST SCENARIOS)
   ↓
5. TECHNICAL: "Any technical constraints?"
   ↓
6. SCOPE: "What's in/out of scope?"
   ↓
7. SUMMARIZE: Create PRD summary
   ↓
8. CONFIRM: "Does this capture your requirements?"
```
