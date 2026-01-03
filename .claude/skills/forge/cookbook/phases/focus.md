# Focus Phase 🎯

**Purpose**: Clarity - Define WHAT you're building and WHY
**Lead Agents**: Architect, Security, Documentation

## Core Question

> "What problem are we solving and for whom?"

## Goals

1. Define the specific problem statement (not vague goals)
2. Identify target users (not "everyone")
3. Write testable success criteria ("loads in <2s" not "should be fast")
4. Create System Context diagram (C4 Level 1)
5. Define clear boundaries - what you WON'T build

## MANDATORY: Test Scenarios First

**No design or code without test scenarios.**

Before any architecture work, define:
- What are the expected inputs and outputs?
- What are the success criteria?
- What edge cases exist?
- How will we know it's working?

## Tasks Checklist

- [ ] **Define problem statement** - Specific problem, not vague goals
- [ ] **Identify target users** - Who exactly benefits?
- [ ] **Write success criteria** - Testable, measurable outcomes
- [ ] **Define test scenarios** (MANDATORY) - How will we verify success?
- [ ] **Create System Context (C4 L1)** - System boundaries and actors
- [ ] **Define constraints** - What we WON'T build
- [ ] **Identify security risks** - What could go wrong?
- [ ] **Create/Update PRD** - Document decisions

## Agent Contributions

### Architect Agent (Primary)
Focus on:
- Specific problem statement (not vague goals)
- Target users (not "everyone")
- Testable success criteria ("loads in <2s" not "should be fast")
- System Context diagram (C4 Level 1)
- Clear boundaries - what you WON'T build

### Security Agent
Focus on:
- Threat modeling
- Authentication/authorization needs
- Data protection requirements
- Compliance considerations

### Documentation Agent
Focus on:
- PRD creation/updates
- Requirements documentation
- Decision records

## Test Scenario Format

```gherkin
Feature: [Feature Name]

Scenario: [Happy path description]
  Given [initial context]
  When [action taken]
  Then [expected result]

Example:
  Input: [Concrete input value]
  Output: [Expected output value]

Scenario: [Edge case description]
  Given [initial context]
  When [edge case action]
  Then [expected handling]

Scenario: [Error case description]
  Given [initial context]
  When [error condition]
  Then [error handling]
```

## Validation Gate

Before advancing to Orchestrate, verify:

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

**Must have:**
- [ ] Problem statement defined (specific, not vague)
- [ ] Target users identified
- [ ] Test scenarios completed
- [ ] Success criteria are testable
- [ ] System Context (C4 L1) documented
- [ ] Security risks identified

## Commands

```bash
# Mark task complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "test scenarios"

# Add additional task
uv run .claude/skills/forge/tools/forge_phase.py add-task "Review with stakeholders"

# Check if ready to advance
uv run .claude/skills/forge/tools/forge_status.py --validate

# Advance to Orchestrate
uv run .claude/skills/forge/tools/forge_phase.py advance
```

## Common Mistakes

1. **Jumping to implementation** - Stay focused on WHAT and WHY, not HOW
2. **Skipping test scenarios** - This will block phase advancement
3. **Vague requirements** - "Should be fast" is not testable
4. **Ignoring security** - Address risks early, not after implementation
5. **Building for "everyone"** - Be specific about who this is for
6. **No clear boundaries** - Define what you WON'T build
