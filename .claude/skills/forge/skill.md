# FORGE Framework Skill

AI-first development framework with 5-phase structured cycles.
Use when: "forge", "new cycle", "phase", "advance phase", "invoke agent", "checkpoint", "development task", "implement", "build feature"

## Variables

```yaml
enable_focus_phase: true
enable_orchestrate_phase: true
enable_refine_phase: true
enable_generate_phase: true
enable_evaluate_phase: true
enable_learning_system: true
strict_validation: true
auto_context: true
```

## Purpose

Structure development into 5 sequential phases (Focus → Orchestrate → Refine → Generate → Evaluate) using Python CLI tools. Manages `.forge/` state directly - no MCP server required.

**Core Principle**: Test scenarios MUST be defined before any code is written.

## Auto-Context (ALWAYS RUN FIRST)

Before ANY development-related action, establish FORGE context:

1. **Check for .forge/ directory**
   - If missing: Suggest `uv run tools/forge_init.py` before proceeding
   - If exists: Continue to step 2

2. **Get current state**
   ```bash
   uv run .claude/skills/forge/tools/forge_status.py --json
   ```

3. **From the status, note:**
   - Active cycle(s) and feature name
   - Current phase (Focus/Orchestrate/Refine/Generate/Evaluate)
   - Phase progress and incomplete tasks
   - Blocking issues

4. **Apply phase context to user's request:**
   - If in Focus: Ensure test scenarios before any design/code discussion
   - If in Orchestrate: Frame work as task breakdown
   - If in Refine: Enforce TDD (tests first, then implementation)
   - If in Generate: Focus on build/deployment/docs
   - If in Evaluate: Gather metrics and learnings

5. **Read current phase cookbook:**
   - `cookbook/phases/{current-phase}.md`

This ensures every interaction respects the current FORGE state.

## Instructions

Based on user request, determine which action to take:

### Initialization
If user requests "forge init" or "initialize forge":
- Run: `uv run .claude/skills/forge/tools/forge_init.py`
- Creates `.forge/` directory with config, templates, learnings

### New Cycle
If user requests "new cycle", "start cycle", "forge new":
- Read: `cookbook/workflows/new-cycle.md`
- Run: `uv run .claude/skills/forge/tools/forge_cycle.py new "feature-name" --priority medium`
- Then read: `cookbook/phases/focus.md` to guide Focus phase

### Status Check
If user requests "status", "forge status", "what phase":
- Run: `uv run .claude/skills/forge/tools/forge_status.py`
- Shows all active cycles with phase progress

### Checkpoint/Validate
If user requests "checkpoint", "validate", "can I advance":
- Run: `uv run .claude/skills/forge/tools/forge_status.py --validate`
- Reports blocking issues and warnings

### Phase Advance
If user requests "advance", "next phase", "phase advance":
- First run: `uv run .claude/skills/forge/tools/forge_status.py --validate`
- If valid, run: `uv run .claude/skills/forge/tools/forge_phase.py advance`
- Read next phase cookbook: `cookbook/phases/{next-phase}.md`

### Complete Task
If user requests "complete task", "mark done", "task done":
- Run: `uv run .claude/skills/forge/tools/forge_phase.py complete-task "task description"`

### Add Task
If user requests "add task", "new task":
- Run: `uv run .claude/skills/forge/tools/forge_phase.py add-task "task description"`

### Development Work (Implementation Requests)
If user requests implementation work ("build", "implement", "create", "add feature"):
- FIRST: Run auto-context to get current phase
- If NOT in Refine phase: Warn user and suggest completing earlier phases
- If in Refine phase: Proceed with TDD approach (tests first)
- Read: `cookbook/agents/developer.md` for implementation guidance

### Agent Invocation
If user requests "invoke agent", "use architect", "need developer":
- Read: `cookbook/agents/{agent-type}.md`
- Apply agent role and expertise to current task
- Agents: architect, developer, tester, devops, security, documentation, reviewer

### Learning System
If user requests "add learning", "capture insight":
- Run: `uv run .claude/skills/forge/tools/forge_learn.py add <category> "title" "description"`
- Categories: success, failure, pattern, antipattern, tool, process

### Retrospective
If user requests "retrospective", "retro", "cycle review":
- Run: `uv run .claude/skills/forge/tools/forge_learn.py retro`
- Guide user through reflection prompts

### Complete Cycle
If user requests "complete cycle", "finish cycle", "archive cycle":
- First validate: `uv run .claude/skills/forge/tools/forge_status.py --validate`
- Run: `uv run .claude/skills/forge/tools/forge_cycle.py complete <cycle-id>`

## Workflow

1. **Context** - Run auto-context to understand current FORGE state
2. **Understand** - Parse user's request in context of current phase
3. **Route** - Select appropriate cookbook (progressive disclosure)
4. **Execute** - Run Python CLI tools via `uv run`
5. **Validate** - Check phase gates before state changes
6. **Guide** - Provide phase-appropriate next steps

## The 5 FORGE Phases

| Phase | Icon | Purpose | Lead Agents |
|-------|------|---------|-------------|
| Focus | 🎯 | Requirements, test scenarios, architecture | Architect, Security, Documentation |
| Orchestrate | 📝 | Task breakdown, dependencies, test strategy | Architect, DevOps, Tester |
| Refine | 🔨 | TDD implementation (RED-GREEN-REFACTOR) | Developer, Tester, Reviewer |
| Generate | 🚀 | Build artifacts, deployment, final docs | DevOps, Documentation, Tester |
| Evaluate | 📊 | Metrics, retrospective, learnings | All Agents |

## Phase-Aware Behavior

### When in Focus Phase
- Block any code implementation requests
- Redirect to: requirements gathering, test scenario definition, architecture design
- Say: "We're in Focus phase. Let's define test scenarios before any implementation."

### When in Orchestrate Phase
- Block implementation requests
- Redirect to: task breakdown, dependency mapping, test strategy
- Say: "We're in Orchestrate phase. Let's break this into specific tasks first."

### When in Refine Phase
- ALLOW implementation, but enforce TDD
- For any feature: Write test first → Run test (RED) → Implement → Run test (GREEN) → Refactor
- Say: "Let's write the test for this feature first."

### When in Generate Phase
- Focus on build, deployment, documentation
- Block new feature requests
- Say: "We're in Generate phase. Let's finalize the build and docs."

### When in Evaluate Phase
- Focus on metrics, retrospective, learnings
- Block new work
- Say: "We're in Evaluate phase. Let's capture what we learned."

## Phase Gates (Mandatory Before Advancing)

### Focus → Orchestrate
- [ ] Test scenarios defined (MANDATORY)
- [ ] Architecture designed
- [ ] Security risks identified

### Orchestrate → Refine
- [ ] Minimum 3 tasks defined
- [ ] Dependencies mapped
- [ ] Test strategy documented

### Refine → Generate
- [ ] Tests written and passing
- [ ] Code review completed
- [ ] All implementation tasks done

### Generate → Evaluate
- [ ] Build artifacts created
- [ ] Documentation updated

### Evaluate → Complete
- [ ] Success metrics collected
- [ ] Retrospective conducted (recommended)

## Examples

| User Says | Action |
|-----------|--------|
| "Initialize forge in this project" | `uv run tools/forge_init.py` |
| "Start a new cycle for user authentication" | `uv run tools/forge_cycle.py new "user-authentication"` |
| "What's my current status?" | `uv run tools/forge_status.py` |
| "Can I advance to the next phase?" | `uv run tools/forge_status.py --validate` |
| "Advance to orchestrate phase" | `uv run tools/forge_phase.py advance` |
| "Mark test scenarios as complete" | `uv run tools/forge_phase.py complete-task "test scenarios"` |
| "I need the architect agent" | Read `cookbook/agents/architect.md`, apply expertise |
| "Add a learning about TDD" | `uv run tools/forge_learn.py add pattern "TDD" "description"` |
| "Run a retrospective" | `uv run tools/forge_learn.py retro` |
| "Complete this cycle" | `uv run tools/forge_cycle.py complete <id>` |
| "Let's implement the login feature" | Check phase → If Refine: TDD approach; If not: redirect to current phase |

## Tool Reference

| Tool | Command | Purpose |
|------|---------|---------|
| forge_init.py | `uv run tools/forge_init.py` | Initialize .forge/ |
| forge_cycle.py | `uv run tools/forge_cycle.py new\|list\|show\|complete` | Manage cycles |
| forge_phase.py | `uv run tools/forge_phase.py advance\|complete-task\|add-task\|validate` | Manage phases |
| forge_status.py | `uv run tools/forge_status.py [--validate]` | Get status |
| forge_learn.py | `uv run tools/forge_learn.py add\|list\|retro` | Manage learnings |
