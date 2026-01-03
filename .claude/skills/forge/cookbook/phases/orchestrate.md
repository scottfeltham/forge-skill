# Orchestrate Phase 📋

**Purpose**: Planning - Break the feature into AI-manageable pieces
**Lead Agents**: Architect, DevOps, Tester

## Core Question

> "How do we break this into session-sized tasks with clear dependencies?"

## Goals

1. Design Container architecture (C4 Level 2) - deployable units
2. Design Component architecture (C4 Level 3) - internal structure
3. Create Dependency Map - what must exist before what
4. Break into session-sized tasks - one task per AI session

## C4 Architecture Diagrams

### Level 2: Container Diagram
Shows the high-level technology choices and how containers communicate:
- Web applications, APIs, databases
- Message queues, file systems
- External services

### Level 3: Component Diagram
Shows internal structure of each container:
- Services, controllers, repositories
- Internal interfaces and relationships

## Tasks Checklist

- [ ] **Container architecture (C4 L2)** - Deployable units and communication
- [ ] **Component architecture (C4 L3)** - Internal structure of containers
- [ ] **Create dependency map** - What depends on what?
- [ ] **Break into session-sized tasks** - One task per AI session
- [ ] **Define test strategy** - Unit, integration, e2e approach
- [ ] **Identify infrastructure needs** - CI/CD, environments

## Task Sizing Guidelines

Each task should be:
- **Session-sized** - Completable in a single AI session
- **Specific** - Clear definition of done
- **Testable** - Verifiable outcome
- **Independent** - Minimal dependencies where possible

### Good Task Examples
- "Implement user login endpoint with JWT validation"
- "Write unit tests for authentication service"
- "Create database migration for users table"

### Bad Task Examples
- "Build auth system" (too large)
- "Make it work" (not specific)
- "Everything for login" (too vague)

## Agent Contributions

### Architect Agent (Primary)
Focus on:
- Container architecture (C4 Level 2)
- Component architecture (C4 Level 3)
- Component interfaces and contracts
- Technical dependencies

### DevOps Agent
Focus on:
- CI/CD pipeline needs
- Deployment dependencies
- Infrastructure requirements
- Environment configuration

### Tester Agent
Focus on:
- Test coverage strategy
- Test environment needs
- Test data requirements
- Automation approach

## Dependency Mapping

Identify:
1. **Technical dependencies** - Libraries, services, APIs
2. **Task dependencies** - Which tasks must complete first
3. **External dependencies** - Other teams, third parties

```
Task A (no dependencies)
  └── Task B (depends on A)
       └── Task C (depends on B)
Task D (parallel to A)
```

## Test Strategy Template

```markdown
## Test Strategy for [Feature]

### Unit Tests
- [ ] [Component A] - [What to test]
- [ ] [Component B] - [What to test]

### Integration Tests
- [ ] [Integration point] - [What to test]

### E2E Tests
- [ ] [User flow] - [What to test]

### Test Data
- [Required test data/fixtures]

### Test Environment
- [Environment requirements]
```

## Validation Gate

Before advancing to Refine, verify:

```bash
uv run .claude/skills/forge/tools/forge_status.py --validate
```

**Must have:**
- [ ] Container diagram (C4 L2) documented
- [ ] Component diagram (C4 L3) documented
- [ ] Minimum 3 session-sized tasks defined
- [ ] Dependencies mapped
- [ ] Test strategy defined

## Commands

```bash
# Add tasks
uv run .claude/skills/forge/tools/forge_phase.py add-task "Implement login endpoint"
uv run .claude/skills/forge/tools/forge_phase.py add-task "Write unit tests for auth"
uv run .claude/skills/forge/tools/forge_phase.py add-task "Create user database schema"

# Mark planning tasks complete
uv run .claude/skills/forge/tools/forge_phase.py complete-task "container architecture"
uv run .claude/skills/forge/tools/forge_phase.py complete-task "map dependencies"

# Validate and advance
uv run .claude/skills/forge/tools/forge_status.py --validate
uv run .claude/skills/forge/tools/forge_phase.py advance
```

## Common Mistakes

1. **Tasks too large** - Break down further if not completable in one session
2. **Missing test tasks** - Every feature task should have corresponding test tasks
3. **Ignoring dependencies** - Map them even if they seem obvious
4. **Starting implementation** - Stay in planning mode until phase advances
5. **Skipping C4 diagrams** - Architecture must be documented before coding
