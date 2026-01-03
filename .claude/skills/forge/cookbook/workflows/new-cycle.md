# New Cycle Workflow

Start a new FORGE development cycle.

## Prerequisites

- FORGE initialized in project (`uv run tools/forge_init.py`)
- Clear understanding of the feature/goal

## Steps

### 1. Create the Cycle

```bash
uv run .claude/skills/forge/tools/forge_cycle.py new "feature-name" --priority medium
```

**Options:**
- `--priority`: low, medium, high, critical
- `--description`: Add initial description

### 2. Verify Creation

```bash
uv run .claude/skills/forge/tools/forge_status.py
```

You should see:
- New cycle listed
- Status: Focus
- Phase 1 tasks ready

### 3. Enter Focus Phase

Read the Focus phase guide:
- `cookbook/phases/focus.md`

Start with:
1. **Requirements gathering** - What problem are we solving?
2. **Test scenarios** - How will we know it works?
3. **Architecture design** - How will we build it?

### 4. Invoke Appropriate Agents

For Focus phase:
```
- Read cookbook/agents/architect.md for design work
- Read cookbook/agents/security.md for risk assessment
- Read cookbook/agents/documentation.md for PRD creation
```

## Example Session

```
User: "Start a new cycle for user authentication"

Agent Actions:
1. Run: uv run tools/forge_cycle.py new "user-authentication" --priority high
2. Output: Created cycle user-authentication-20240115
3. Run: uv run tools/forge_status.py
4. Output: Shows cycle in Focus phase
5. Say: "Cycle created. We're in Focus phase. Let's start by defining test scenarios for authentication. What authentication methods do you need?"
```

## Conversational PRD Building

When starting a cycle, guide the user through requirements:

### Questions to Ask

**User Context**
- Who will use this feature?
- What problem does it solve for them?

**Success Criteria**
- How will we know it's working?
- What does success look like?

**Technical Constraints**
- Any existing systems to integrate?
- Performance requirements?
- Security requirements?

**Scope**
- What's in scope for this cycle?
- What's explicitly out of scope?

## Tips

1. **Be specific with names** - "user-authentication" not "auth"
2. **Set appropriate priority** - Affects attention and urgency
3. **Don't skip to code** - Focus phase must define test scenarios first
4. **Document early** - Capture decisions as you make them
