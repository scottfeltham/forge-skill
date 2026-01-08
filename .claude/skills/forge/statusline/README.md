# FORGE Status Line for Claude Code

A custom status line script that displays FORGE development cycle information in Claude Code.

## What It Shows

When in a FORGE project:
```
Refine: my-feature │ Opus 4.5 │ main* │ 14:30
```

- **Phase**: Current FORGE phase (Focus, Orchestrate, Refine, Generate, Evaluate)
- **Cycle**: Active development cycle name
- **Model**: Current Claude model
- **Branch**: Git branch with `*` if uncommitted changes
- **Time**: Current time

When not in a FORGE project:
```
project-name │ Opus 4.5 │ main │ 14:30
```

## Installation

1. Copy the script to your Claude config directory:
   ```bash
   cp statusline-forge.sh ~/.claude/statusline-forge.sh
   chmod +x ~/.claude/statusline-forge.sh
   ```

2. Update your Claude Code settings (`~/.claude/settings.json`):
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "bash ~/.claude/statusline-forge.sh"
     }
   }
   ```

3. Restart Claude Code to see the new status line.

## How It Works

The script:
1. Receives JSON input from Claude Code with workspace and model info
2. Walks up the directory tree looking for a `.forge` directory
3. If found, reads the most recent active cycle file
4. Extracts the current phase from the `**Status**:` line
5. Displays phase + cycle name in the status line

## Requirements

- `jq` for JSON parsing
- `bash` shell
- Git (optional, for branch display)
